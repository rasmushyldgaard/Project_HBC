""" 
Module for planning the charge plan for a home battery 

Date:
    26-09-2023

"""
# pylint: skip-file

import pandas as pd
import numpy as np
import math
from typing import Any

from controller.collector import Collector
from controller.enums import ActionReason, SolarStrategy

COLUMNS = ['Time', 'Action', 'SolarSurplus', 
           'ElNetCharge', 'BatteryDelta', 'BatteryExpected',
           'SolarExport', 'ActionReason']
BATTERY_PRICE_INDEX_THRESHOLD = 10

# UsePrice (up), BuyPrice (bp), Effectivity (ef) -> PriceIndex
price_index = lambda up, bp, ef : math.floor((up * ef - bp) * 100)
""" Calculate our own price index based on the electric power price of the hour
    being looked at and the price of a potential charging hour in combination with the
    effectiveness of the system/how much energy is being retained through charging and 
    using the energy from the battery. The index tells how much is earned per kWh that
    goes through the battery -in ører (DKK*100). 
    up (UsePrice) and bp (BuyPrice) is in DKK, therefore we have to multiply by 100.
"""

class Planner(Collector):
    """ Class for calculating the charge plan """

    def __init__(self, settings: dict[str, Any]):
        super().__init__(settings)
        self._max_charge_rate = settings["max_rate"]
        self._max_capacity = settings["capacity"]
        self._min_capacity = settings["threshold"]
        self._battery_effectivity = settings["effectivity"]
        self._solar_strategy = settings["solar_strategy"]
        self._output_frame = pd.DataFrame()
        self._main()

    @property
    def plan(self) -> pd.DataFrame:
        """ Get the charge plan """
        return self._output_frame

    def _main(self) -> None:
        """ Main function of Planner """
        # Create an empty DataFrame template
        temp_output = pd.DataFrame(columns=COLUMNS)
        temp_output['Time'] = self.data.loc[:, 'Time']
        temp_output = temp_output.fillna(0.0)
        temp_output['Action'] = ''
        temp_output['ActionReason'] = ''

        # Start index
        calc_start_index = 0

        # fill in the empty part of temp_output
        self._battery_first_calculation( temp_output, calc_start_index )
        # guess we could check for low limit violation before or after first calculation. 
        # Choose to do it after.
        violation = self._battery_check_if_below_minimum_charge( temp_output, 0 )
        if violation[0] is not None:
            # This violation should only be possible if battery starts with below minimum value:
            # Minimum bar was raised or power went out and battery supplied energy for the house.
            self._battery_refill_buffer_immidiately( temp_output, violation )
                

        # check if we charged above maximum with solar generated power and fix it.
        violation = self._battery_check_if_above_maximum_charge( temp_output, calc_start_index )
        while violation[0] is not None: # TODO: Avoid endless loop?
            # Until we are below maximum everywhere, find out to spend energy or sell it
            self._battery_fix_excess( temp_output, violation )
            violation = self._battery_check_if_above_maximum_charge( temp_output, calc_start_index )
            # is it possible to make sure that we cannot get trapped in loop - if some error occurs?

        # Use total area and find actions:
        calc_area = self.data.loc[ calc_start_index : self.data.index.values.size ]
        # print( f"Calc area:\n {calc_area}")
        temp_output = self._set_peak_actions_automatic_v2( calc_area, temp_output )

        # Should we sell combined solar surplus over the day?
        self._solar_sell_timeframe_surplus( temp_output )

        # See if high spotprice allows to sell solar and buy cheaper electricity from net
        temp_output = self._solar_decide_sell_or_use( temp_output )

        # run test to make sure there are no violations:
        violation = self._battery_check_if_above_maximum_charge( temp_output, 0 )
        if violation[0] is not None:
            print( f"Violation of battery bounds found at index {violation[0]} and \
                  value {violation[1]}" )
        violation = self._battery_check_if_below_minimum_charge( temp_output, 0 )
        if violation[0] is not None:
            print( f"Violation of battery bounds found at index {violation[0]} and \
                  value {violation[1]}" )

        # save to output
        self._output_frame = temp_output


    # set load plan action or output action
    def _set_loadplan_action( self, output_frame: pd.DataFrame, index: int, action: str, 
                              charge_amount: float = None ) -> None: 
        """ Set action in the output frame. """
        # Later on should probably do stuff depending on what action is changed from and to!
        if action == 'charge':
            # get amount to charge
            if charge_amount is None:
                to_charge = self._max_charge_rate
            else:
                to_charge = charge_amount
            success = self._set_charge_at_index( index, output_frame, to_charge )
            if not success:
                print ( f"Failed to set loadplan action \"charge\" @ index {index}")

        else:
            if output_frame.at[ index, "Action" ] == 'charge':
                output_frame.at[ index, "ElNetCharge" ] = 0.0
            output_frame.at[ index, "Action" ] = action         
            self._recalculate_delta_and_battery_level( output_frame, index )
            self._calculate_solar_export( output_frame, index )


    def _set_peak_actions_automatic_v2( self, 
                                        peak_area: pd.DataFrame,  
                                        output_frame: pd.DataFrame ) -> pd.DataFrame:
        """ Function for trying to equalize as much as possible in peak hours
        Parameters:
        argument1 (pd.DataFrame): The peak area cutout from the input data
        argument2 (pd.DataFrame): The cutout of the available charging hours
        argument3 (pd.DataFrame): The output DataFrame to insert calculated actions into
        
        Returns:
        None: No return. 
        pd.DataFrame: With set actions"""
        result = output_frame

        # sort the prices
        peak_sorted = peak_area.sort_values( 'Price', ascending=False, inplace=False )
        # go through calculating worth for each hour
        peak_indices = peak_sorted.index.values
        for x in peak_indices:
            # if idle use power -> equalize ? possible to use battery?
            # changed = False
            if result.at[ x, "Action" ] == 'idle':
                # equalize if we consume electricity - if surplus positive and idle, we decided to
                # sell the electricity.
                if result.at[ x, "SolarSurplus" ] < 0.0: 
                    # check if enough juice on the batteries!
                    enough_battery = self._battery_check_equalize_possible( result, x)
                    if enough_battery:
                        self._set_loadplan_action( result, x, 'equalize') 
                        #add reason
                        self._set_action_reason( result, x, ActionReason.EQUALIZE_USE_BATTERY )
                    else: 
                        # need to test if we can charge enough to equalize!
                        charge_test = self._try_to_get_charge( result, x)
                        if charge_test[0]:
                            result = pd.DataFrame(charge_test[1], copy=True)               
        return result
    

    def _battery_first_calculation( self, output_frame: pd.DataFrame, start_index: int = 0,
                                   stop_index: int = None ) -> float:
        """ First we expect to charge all surplus solar power to battery, set surplus hours to 
        equalize and we have a first view of the battery """
        if stop_index:
            stop = stop_index
        else:
            stop = output_frame.index.values.size
        for index in range( start_index, stop ):
            self._battery_calculate_solar_surplus( output_frame, index )
            if output_frame.at[ index, "SolarSurplus" ] > 0:
                self._set_loadplan_action( output_frame, index, 'equalize')
                # output_frame.at[ index, "Action" ] = 'equalize'
                self._set_action_reason( output_frame, index, 
                                        ActionReason.EQUALIZE_SOLAR_CHARGE)
            else:
                self._set_loadplan_action( output_frame, index, 'idle')
                # output_frame.at[ index, "Action" ] = 'idle'
                self._set_action_reason( output_frame, index, 
                                        ActionReason.IDLE_DEFAULT)
            self._battery_calculate_delta_value( output_frame, index )
            self._battery_calculate_expected_level( output_frame, index )
            self._calculate_solar_export( output_frame, index )
        

    def _battery_calculate_solar_surplus( self, output_frame: pd.DataFrame, 
                                         index: int ) -> None:
        """ Calculate the solar surplus generation. Solar minus expected consumption """
        surplus = self._data.at[ index, "Power"] - self._data.at[ index, "ExpectedConsumption"]
        output_frame.at[ index, "SolarSurplus" ] = round(surplus, 4 )


    def _calculate_solar_export( self, output_frame: pd.DataFrame, index: int ) -> None:
        """ Calculate the solar export. How much kWh are exported at the specific hour"""
        if output_frame.at[ index, "Action" ] == 'idle':
            if output_frame.at[ index, "SolarSurplus" ] > 0:
                output_frame.at[ index, "SolarExport" ] = output_frame.at[ index, "SolarSurplus" ]
            else:
                output_frame.at[ index, "SolarExport" ] = 0.0
        else: # "Action" == 'equalize', should not technically sell anything in charge since only 
            # when also need from the net.
            if output_frame.at[ index, "SolarSurplus" ] > self._max_charge_rate:
                output_frame.at[ index, "SolarExport" ] = output_frame.at[ index, "SolarSurplus" ] \
                                                          - self._max_charge_rate
            else: 
                output_frame.at[ index, "SolarExport" ] = 0.0


    def _battery_calculate_delta_value( self, output_frame: pd.DataFrame, 
                                         index: int) -> None:
        """ What is the Battery Delta """

        if output_frame.at[ index, "Action" ] == 'idle':
            output_frame.at[ index, "BatteryDelta" ] = 0.0

        elif output_frame.at[ index, "Action" ] == 'equalize':
            if output_frame.at[ index, "SolarSurplus" ] > self._max_charge_rate:
                output_frame.at[ index, "BatteryDelta" ] = self._max_charge_rate
            else:
                output_frame.at[ index, "BatteryDelta" ] = output_frame.at[ index, "SolarSurplus" ]

        elif output_frame.at[ index, "Action" ] == 'charge':
            if output_frame.at[ index, "SolarSurplus" ] < 0.0:
                output_frame.at[ index, "BatteryDelta" ] = output_frame.at[ index, "ElNetCharge" ]
            elif output_frame.at[ index, "SolarSurplus" ] > self._max_charge_rate:
                output_frame.at[ index, "BatteryDelta" ] = self._max_charge_rate
            else:
                output_frame.at[ index, "BatteryDelta" ] = output_frame.at[ index, "SolarSurplus" ]\
                                                           + output_frame.at[ index, "ElNetCharge" ]


    def _battery_calculate_expected_level( self, output_frame: pd.DataFrame, 
                                         index: int) -> None:
        """ Calculate what the expected battery level value will be. """
        if index == 0:
            # battery_level = self._battery_get_current_charge_level()
            output_frame.at[ index , "BatteryExpected" ] = self._battery_get_current_charge_level()
        else:
            battery_expected = output_frame.at[ index - 1, "BatteryExpected" ] + \
                               output_frame.at[ index - 1, "BatteryDelta" ]
            output_frame.at[ index ,"BatteryExpected" ] = round(battery_expected,
                                                                4)
                                                
            # battery_level = output_frame.at[ index - 1, "BatteryExpected" ]
        # output_frame.at[ index , "BatteryExpected" ] = battery_level + \
        #                                                output_frame.at[ index, "BatteryDelta" ]

    # TODO: Fix this
    def _battery_get_current_charge_level( self ) -> float:
        """ Get the current battery level from MiniCon """
        # dummy so far
        return 0.0      


    def _battery_check_if_above_maximum_charge( self, output_frame: pd.DataFrame, 
                                         index_begin: int) -> tuple:
        """ Check from index_begin and forward if too much charging has been planned """
        result = (None, None)
        for index in range( index_begin, output_frame.index.values.size ):
            if output_frame.at[ index, "BatteryExpected" ] > self._max_capacity:
                excess = output_frame.at[ index, "BatteryExpected" ] - self._max_capacity
                result = ( index, excess )
                break
        return result
        

    def _battery_check_if_below_minimum_charge( self, output_frame: pd.DataFrame, 
                                         index_begin: int) -> tuple:
        """ Check from index_begin and forward if too much powerdraw empties and would pull 
        battery level negative.
        Need to check that battery will not go negative after last hour!
        
        Returns:
        violation - lacking amount is returned as absolute value, so positive lacking amount
        """
        result = (None, None)
        end_of_range = output_frame.index.values.size
        for index in range( index_begin, end_of_range): #output_frame.index.values.size ):
            if output_frame.at[ index, "BatteryExpected" ] < self._min_capacity:
                lacking = output_frame.at[ index, "BatteryExpected" ] - self._min_capacity
                absolute_lacking = abs(lacking)
                if absolute_lacking > 0.001:
                    result = ( index, absolute_lacking )
                    break
        # to fix bug that equalize can use battery with no electricity on it.
        if result[0] is None:
            last_index = end_of_range - 1
            surplus = output_frame.at[ last_index, "SolarSurplus" ]
            if output_frame.at[ last_index, "Action" ] == 'equalize' and surplus < 0 :
                # capacity must be positive, since result is None
                capacity = output_frame.at[ last_index, "BatteryExpected" ] - \
                           self._min_capacity
                lacking = abs( surplus ) - capacity
                if lacking > 0 :
                    result = ( last_index, lacking ) 

        return result
    

    def _battery_fix_excess( self, output_frame: pd.DataFrame, violation: tuple ) -> None:
        """ Function to fix trying to over charge the battery - 
            thought to happen if "too much" solar
            TODO: Make error checking and check if lists or dataframes are empty"""
        remaining_excess = violation[1]
        index_of_violation = violation[0]
        zero_point = 0
        # get period from zero/minimum point -> index of violation
        for x in range ( index_of_violation -1, 0, -1 ):
            if output_frame.at[ x, "BatteryExpected" ] <= self._min_capacity:
                zero_point = x
                break
        price_area_to_check = self._data.loc[ zero_point: index_of_violation ]
        # find the best place to spend excess, point a  ( use prices to )
        filt_area = output_frame.loc[ zero_point: index_of_violation ]
        # add test for surplus to only get where we can actually spend energy!
        filt = (filt_area["Action"] == 'idle') & (filt_area["SolarSurplus"] < 0.0)
        price_filtered = price_area_to_check.loc[ filt ]
        price_sorted = price_filtered.sort_values( "Price", ascending=False )

        for x in range( price_sorted.index.values.size ):
            point_a = price_sorted.index.values[ x ]
            # find minimum battery level from point a -> index , "min-value"
            min_value = self._get_battery_minimum_between_indices( output_frame, 
                                                                  point_a, index_of_violation )
            min_value = min_value - self._min_capacity
            # if "min-value" > expected consumption, spend full EC at point a, else only min-value
                # if excess > EC, full EC, else excess. ( guess we cannot really control this atm)
            # Adjust excess and repeat pattern
            # use solarsurplus to get actual expected switch value!
            expected_consumption = abs( output_frame.at[ point_a, "SolarSurplus" ])
            if min_value > expected_consumption: 
                self._set_loadplan_action( output_frame, point_a, 'equalize' )
                self._set_action_reason( output_frame, point_a, 
                                        ActionReason.EQUALIZE_USE_BATTERY )
                remaining_excess -= expected_consumption
            #else:
                # consumption would put batt under minimum -> we skip this option
            if remaining_excess <= 0:
                break  

        # if we used EC and still excess, repeat pattern but with stopping charging/
        # stop equalizing with solar!
        if remaining_excess > 0:
            # start selling solar!
            #TODO: implement - tried below
            # find the best place to sell excess, point a  ( use prices to )
            df = output_frame.loc[ zero_point: index_of_violation ]
            filt = (df["Action"] == 'equalize') & (df["SolarSurplus"] > 0.0)
            spotprice_filtered = price_area_to_check.loc[ filt ]
            spotprice_sorted = spotprice_filtered.sort_values( "SpotPrice", ascending=False )
            for x in range( spotprice_sorted.index.values.size ):
                point_a = spotprice_sorted.index.values[ x ]
                min_value = self._get_battery_minimum_between_indices( output_frame, 
                                                                  point_a, index_of_violation )
                min_value = min_value - self._min_capacity
                solar_surplus = output_frame.at[ point_a, "SolarSurplus" ]
                if min_value > solar_surplus: # we can ditch solar without going negative
                    self._set_loadplan_action( output_frame, point_a, 'idle' )
                    self._set_action_reason( output_frame, point_a, 
                                        ActionReason.IDLE_SOLAR_OVERFLOW )
                    remaining_excess -= solar_surplus
                #else:
                    # consumption would put batt under minimum -> we skip this option
                if remaining_excess <= 0:
                    break  
            

    def _battery_fix_lacking( self, price_index_creating_violation: int, 
                             output_frame: pd.DataFrame, violation: tuple ) -> float:
        """ Function to fix trying to decharge the battery below minimum"""
        price_to_calculate_against = self.data.at[ price_index_creating_violation, "Price"]
        remaining_lacking = violation[1] # changed function to return lacking as absolute value!
        index_of_violation = violation[0]
        max_point = 0
        # get period from 100%/maximum point -> index of violation
        for x in range ( index_of_violation -1, 0, -1 ):
            if output_frame.at[ x, "BatteryExpected" ] >= self._max_capacity:
                max_point = x
                break
        price_area_to_check = self._data.loc[ max_point: index_of_violation - 1 ]
        # filter to remove the price index creating the violation !
        filt = price_area_to_check.index.values != price_index_creating_violation
        price_area_to_check_without_violator = price_area_to_check.loc[filt]
        # find the best place to charge, point a  ( use prices to )
        # price_sorted =price_area_to_check.sort_values( "Price" )
        price_sorted = price_area_to_check_without_violator.sort_values( "Price" )

        # TODO:
        # if model == SmartBuy:
        #    price_sorted = price_area_to_check_without_violator.sort_values( "Price" )
        # elif model == GreenBuy:
        #   co2_sorted = ...

        for x in range( price_sorted.index.values.size ):
            point_a = price_sorted.index.values[x]
            # only proceed if it makes sense price wise!:
            if price_index(price_to_calculate_against, 
                           self.data.at[ point_a, "Price"], 
                           self._battery_effectivity) > BATTERY_PRICE_INDEX_THRESHOLD:

                # find maximum battery level from point a -> index , "max-value"
                max_value = self._get_battery_maximum_between_indices( output_frame,
                                                                       point_a, index_of_violation )    
                # capacity = MAX - max_value - how much we can charge on the battery maximum 
                capacity = self._max_capacity - max_value
                # find how much we can ACTUALLY charge at point a!
                state = output_frame.at[ point_a, "Action"]
                battery_delta = output_frame.at[ point_a, "BatteryDelta"]
                actual_max = self._max_charge_rate
                actual_min = 0.0  # what we can charge as minimum?!
                # if equalize && surplus negative -> MAX_RATE; 
                # if equalize && surplus positive - MAX - surplus
                # if charge - MAX - BAT_DELTA           if idle -> MAX  
                if ( state == 'equalize' and battery_delta > 0 ) or state == 'charge':
                    actual_max = self._max_charge_rate - battery_delta
                elif ( state == 'equalize' and battery_delta < 0 ):
                    #if we use energy and we change to charge, we actually get a bigger swing -
                    # EC + charge amount!
                    actual_min = abs(battery_delta) # must be positive value, abs of the delta
                    actual_max = self._max_charge_rate + actual_min
                    
                    #TODO: Think of a fail safe to not allow small lacking to stop big use / 
                    # big equalize == big saving

            # if cap > lacking, charge as much as possible at point a, else only cap
                # if possible_charge >= lacking, charge lacking
                # else charge possible charge
            # else ( lacking > cap )
                # if possible_charge > cap -> charge cap
                # else ( possible_charge < cap ) charge possible_charge
                if capacity > remaining_lacking:
                    if actual_max >= remaining_lacking:
                        if remaining_lacking > actual_min:
                            # charge lacking
                            self._set_charge_at_index( point_a, output_frame, remaining_lacking )
                            self._set_action_reason( output_frame, point_a, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                            remaining_lacking = 0.0
                            # print ( "Charge option 1") # Debug
                        elif actual_min > capacity:
                            # do not actually charge
                            # print ( "Charge option 2 - do nothing") # Debug
                            pass
                        else:
                            #charge minimum: actual_min
                            self._set_charge_at_index( point_a, output_frame, actual_min )
                            self._set_action_reason( output_frame, point_a, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                            remaining_lacking -= actual_min
                            # print ( "Charge option 3") # Debug
                    else:
                        # charge actual_max
                        self._set_charge_at_index( point_a, output_frame, actual_max )
                        self._set_action_reason( output_frame, point_a, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                        remaining_lacking -= actual_max
                        # print ( "Charge option 4") # Debug
                else: # capacity <= remaining_lacking
                    if actual_max > capacity:
                        if actual_min > capacity:
                            # do not actually charge
                            # print ( "Charge option 5") # Debug
                            pass
                        else:
                            # charge capacity
                            self._set_charge_at_index( point_a, output_frame, capacity )
                            self._set_action_reason( output_frame, point_a, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                            remaining_lacking -= capacity
                            # print ( "Charge option 6") # Debug
                    else: # actual_max <= capacity
                        # charge actual_max
                        self._set_charge_at_index( point_a, output_frame, actual_max )
                        self._set_action_reason( output_frame, point_a, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                        remaining_lacking -= actual_max
                        # print ( "Charge option 7") # Debug
        # Adjust lacking and repeat pattern as needed

            if remaining_lacking <= 0.0:
                # stop if we have no more lacking
                break
        # if we charged as possible and still lacking, maybe use less electricity if it was 
        # cheaper at some point : SHOULD already be implemented above

        return remaining_lacking

    def _set_action_reason( self, output_frame: pd.DataFrame, 
                           index: int, reason: ActionReason) ->None:
        """Set a reason for the action that will be assigned to the specific hour"""
        output_frame.at[ index, "ActionReason" ] = reason.value


    def _set_charge_at_index( self, index: int, output_frame: pd.DataFrame, 
                             charge_amount: float ) -> bool:
        success = True
        # find state changing from
        previous_state = output_frame.at[ index, "Action" ]
        battery_delta = output_frame.at[ index, "BatteryDelta" ]
        # amount within bounds?
        if previous_state == 'idle':
            if not ( charge_amount >= 0 and charge_amount <= self._max_charge_rate ):
                success = False
        else:
            if not (( charge_amount >= 0 ) and 
                    ( charge_amount + battery_delta ) <= self._max_charge_rate ): 
                success = False

        if success:
            # set 'charge' action
            output_frame.at[ index, "Action" ] = "charge"
            
            if previous_state == 'idle':
                output_frame.at[ index, "ElNetCharge" ] = charge_amount
            elif previous_state == 'charge':
                output_frame.at[ index, "ElNetCharge" ] += charge_amount
            else: # previous_state == 'equalize':
                if battery_delta < 0:
                    if abs(battery_delta) > charge_amount:
                        # we just need to idle and not charge
                        output_frame.at[ index, "Action" ] = "idle"
                    else:
                        output_frame.at[ index, "ElNetCharge" ] = charge_amount + battery_delta
                else:
                    output_frame.at[ index, "ElNetCharge" ] = charge_amount

            # adjust BatteryDelta and rest of dataFrame's BatteryExpected
            self._recalculate_delta_and_battery_level( output_frame, index )
        return success
            

    def _recalculate_delta_and_battery_level( self, output_frame: pd.DataFrame, 
                                              index: int ) -> None:
        self._battery_calculate_delta_value( output_frame, index )
        # add 1, since we only need to calculate again from the next hour.
        for x in range( index + 1, output_frame.index.values.size ):
            # recalculate BatteryExpected
            self._battery_calculate_expected_level( output_frame, x )


    def _get_battery_minimum_between_indices( self, output_frame: pd.DataFrame, 
                                             index_begin: int, index_end: int ) -> float:
        """ Get the lowest battery level between two indices."""
        minimum = min( output_frame.loc[ index_begin : index_end, "BatteryExpected" ] )
        # take into account if index after end would be lower!
        if (index_end == ( output_frame.index.values.size - 1 )) and \
           ( output_frame.at[ index_end, "Action" ] == 'equalize' ) and \
           ( output_frame.at[ index_end, "BatteryDelta" ] < 0.0 ):
            potential_minimum = output_frame.at[ index_end, "BatteryExpected" ] + \
                                output_frame.at[ index_end, "BatteryDelta" ]
            if potential_minimum < minimum:
                minimum = potential_minimum

        return minimum
    

    def _get_battery_maximum_between_indices( self, output_frame: pd.DataFrame, 
                                             index_begin: int, index_end: int ) -> float:
        """ Get the highest battery level between two indices"""
        return max( output_frame.loc[ index_begin : index_end, "BatteryExpected" ] )
    

    def _battery_check_equalize_possible( self, output_frame: pd.DataFrame, 
                                             index_to_equalize: int ) -> bool:
        """Check if it is possible to equalize consumption from battery without charging.
            It is assumed that this is only called when there is overall consumption, that mean
            that SolarSurplus is negative"""
        end_index = output_frame.index.values.size - 1
        minimum_value = self._get_battery_minimum_between_indices( output_frame, 
                                                                  index_to_equalize, end_index )
        minimum_relative_to_buffer = minimum_value - self._min_capacity
        consumption = output_frame.at[ index_to_equalize, "SolarSurplus" ]
        # absolute consumption because it is negative !
        equalize_possible_without_charging = minimum_relative_to_buffer >= abs(consumption)
        return equalize_possible_without_charging
    

    def _try_to_get_charge( self, output_frame: pd.DataFrame, index_to_equalize: int ) -> \
                            tuple[bool, pd.DataFrame]:
        # make dummy dataFrame for the testing
        success = True
        df_to_return = pd.DataFrame()
        dummy_df = pd.DataFrame(output_frame, copy=True)
        # set equalize 
        self._set_loadplan_action( dummy_df, index_to_equalize, 'equalize') 
        self._set_action_reason( dummy_df, index_to_equalize, 
                                        ActionReason.EQUALIZE_USE_BATTERY )
        # check where there is violation for low battery level 
        #               - remember there could be more than one place!
        violation = self._battery_check_if_below_minimum_charge( dummy_df, index_to_equalize )
        # fix is needed 
        while violation[0] is not None:
            lacking_remaining = self._battery_fix_lacking( index_to_equalize, dummy_df, violation )
            if lacking_remaining <= 0.0: # success
                # check if there are more violations
                violation = self._battery_check_if_below_minimum_charge( dummy_df, 
                                                                        index_to_equalize )
            else:
                # could not charge the full necessary amount -> fail
                success = False
                break
        if success:
            df_to_return = dummy_df
        result = ( success, df_to_return )
        return result
    

    def _battery_refill_buffer_immidiately( self, output_frame: pd.DataFrame, 
                                           violation: tuple ) -> None:
        """ Function should charge battery to meet buffer threshold/minimum battery level 
            immediately. A lot of code gotten from fix lacking function and adjusted

            Args:
                output_frame
                violation

        """
        # start from beginning
        elec_needed = violation[1]
        index = 0
        while elec_needed > 0.0:
            # should we start from index 0 -> lets do that to begin with, do not think 
            # it is possible to get violation later unless we save old data.

            capacity = self._max_capacity - output_frame.at[ index, "BatteryExpected"]
            # find how much we can ACTUALLY charge 
            state = output_frame.at[ index, "Action"]
            battery_delta = output_frame.at[ index, "BatteryDelta"]
            actual_max = self._max_charge_rate
            actual_min = 0.0  # what we can charge as minimum?!

            if ( state == 'equalize' and battery_delta > 0 ) or state == 'charge':
                actual_max = self._max_charge_rate - battery_delta
            elif ( state == 'equalize' and battery_delta < 0 ):
                #if we use energy and we change to charge, we actually get a bigger swing -
                # EC + charge amount!
                actual_min = abs(battery_delta) # must be positive value, abs of the delta
                actual_max = self._max_charge_rate + actual_min

            # if cap > lacking, charge as much as possible at point a, else only cap
            # if possible_charge >= lacking, charge lacking
            # else charge possible charge
            # else ( lacking > cap )
            # if possible_charge > cap -> charge cap
            # else ( possible_charge < cap ) charge possible_charge
            if capacity > elec_needed:
                if actual_max >= elec_needed:
                    if elec_needed > actual_min:
                        # charge lacking
                        self._set_charge_at_index( index, output_frame, elec_needed )
                        self._set_action_reason( output_frame, index, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                        elec_needed = 0.0
                        # print ( "Charge option 1") # Debug
                    elif actual_min > capacity:
                        # do not actually charge
                        # print ( "Charge option 2 - do nothing") # Debug
                        pass
                    else:
                        #charge minimum: actual_min
                        self._set_charge_at_index( index, output_frame, actual_min )
                        self._set_action_reason( output_frame, index, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                        remaining_lacking -= actual_min
                        # print ( "Charge option 3") # Debug
                else:
                    # charge actual_max
                    self._set_charge_at_index( index, output_frame, actual_max )
                    self._set_action_reason( output_frame, index, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                    elec_needed -= actual_max
                    # print ( "Charge option 4") # Debug
            else: # capacity <= elec_needed
                if actual_max > capacity:
                    if actual_min > capacity:
                        # do not actually charge
                        # print ( "Charge option 5") # Debug
                        pass
                    else:
                        # charge capacity
                        self._set_charge_at_index( index, output_frame, capacity )
                        self._set_action_reason( output_frame, index, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                        elec_needed -= capacity
                        # print ( "Charge option 6") # Debug
                else: # actual_max <= capacity
                    # charge actual_max
                    self._set_charge_at_index( index, output_frame, actual_max )
                    self._set_action_reason( output_frame, index, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                    elec_needed -= actual_max
                    # print ( "Charge option 7") # Debug

            # Adjust index to go to next hour until done.    
            index += 1

    def _get_charge_amount_available_maximum_at_index( self, output_frame: pd.DataFrame, 
                                                      index: int) -> float:
        """ Find the maximum swing in charge on the battery. 
            Can be higher than max rate, if going from depleting battery to charging

            Args:
                output_frame
                index

            Returns:
                float

        """
        available_charge_max = self._max_charge_rate
        if output_frame.at[ index, "Action" ] == 'idle':
            pass
        else:
            available_charge_max = self._max_charge_rate - \
                                   output_frame.at[ index, "BatteryDelta" ]
        return available_charge_max
        

    def _get_charge_amount_available_minimum_at_index( self, output_frame: pd.DataFrame, 
                                                      index: int) -> float:
        """ Find the minimum swing in charge on the battery. 
            Can be above zero if going from depleting the battery (equalize) to charging

        """
        available_charge_min = 0.0
        battery_delta = output_frame.at[ index, "BatteryDelta" ]
        if output_frame.at[ index, "Action" ] == 'equalize' and battery_delta < 0:
            available_charge_min = abs( battery_delta )
        return available_charge_min
        

    def _decide_charge_amount( self, 
                                minimum_charge_available: float,
                                maximum_charge_available: float,
                                to_upper_limit_in_interval: float,
                                electricity_needed: float ) -> float:
        """ Decide how much to charge at certain index according to the limiting parameters.
            Try to get as much charge as possible at this point without going over limits.
            Then what is left can be gotten at different point.

            Args:
                minimum_charge_available: the minimum swing we can "charge" if we change to charge action
                maximum_charge_available: the maximum swing we can "charge" if we change to charge action
                to_upper_limit_in_interval: the lowest margin towards upper limit in the interval from charge to sell point
                electricity_needed: the amount that we have left, that we want to get charged.

            Returns: 
                The amount that is possible to charge at this specific index.

        """
        result = 0.0
        if to_upper_limit_in_interval > electricity_needed:
            if maximum_charge_available >= electricity_needed:
                if electricity_needed > minimum_charge_available:
                    # charge lacking
                    result = electricity_needed
                    # print ( "Charge option 1") # Debug
                elif minimum_charge_available > to_upper_limit_in_interval:
                    # do not actually charge
                    # print ( "Charge option 2 - do nothing") # Debug
                    pass
                else:
                    #charge minimum: minimum_charge_available
                    # this should result in "too" much charge. buildup in battery.
                    # print ( "Charge option 3") # Debug
                    result = minimum_charge_available 
            else:
                # charge actual_max
                result = maximum_charge_available
                # print ( "Charge option 4") # Debug
        else: # to_upper_limit_in_interval <= electricity_needed
            if maximum_charge_available > to_upper_limit_in_interval:
                if minimum_charge_available > to_upper_limit_in_interval:
                    # do not actually charge
                    # print ( "Charge option 5") # Debug
                    pass
                else:
                    # charge capacity
                    result = to_upper_limit_in_interval 
                    # print ( "Charge option 6") # Debug
            else: # actual_max <= capacity
                # charge actual_max
                result = maximum_charge_available 
                # print ( "Charge option 7") # Debug
        
        return result


    def _solar_decide_sell_or_use( self, output_frame: pd.DataFrame ) -> pd.DataFrame:
        """ Function that decides if solar surplus should be saved in the battery for later use
            or sell it. It makes sense to sell, if it is possible to buy it back at another time
            cheaper. Could potentialle also have an option to sell off an overall surplus, instead
            of filling the battery
            
            Return the resulting dataframe. If no changes, then it should be the same as inputframe
            """
        # Find solar surplus charging times to work on. ( surplus > 0 && equalize ) 
        # Not charge since then there is a need for the power and it has already been decided that
        # it is worthwhile to get the power in that timeslot.
        solar_charging_filter =  ( output_frame[ "SolarSurplus" ] > 0 ) & \
                                 ( output_frame[ "Action" ] == 'equalize' )
        solar_charging_sell_prices = self.data.loc[ solar_charging_filter ]
        solar_sell_prices_sorted = solar_charging_sell_prices.sort_values( 'SpotPrice', \
                                                                           ascending=False )
        # result frame to continuously save successful changes to!
        result_frame = pd.DataFrame( output_frame, copy=True )
        save_result_to_output_frame = False
        # for debug:
        test = solar_sell_prices_sorted[ "SpotPrice"] 

        # loop through the prices
        for sell_index in solar_sell_prices_sorted.index.values:
            dummy_df = pd.DataFrame( result_frame, copy=True ) # dummy to use for operations
            to_continue = False
            # simulate selling
            self._set_loadplan_action( dummy_df, sell_index, 'idle' )
            self._set_action_reason( dummy_df, sell_index, 
                                        ActionReason.IDLE_SOLAR_SELL_HIGH_BUY_LOW)
            # get available charging times before index 
            charge_times_available = self.data.loc[ 0 : sell_index - 1] 
            # sort low to high
            charge_times_sorted = charge_times_available.sort_values( 'Price', ascending=True )
 
            # how much charge we would potentially need to charge
            remaining_necessary_charge = output_frame.at[ sell_index, "BatteryDelta" ]
            first_buy_point = sell_index
            for buy_index in charge_times_sorted.index.values:
                # decide with comparison between sell vs buy price (spotprice vs price)
                if self.data.at[ sell_index, "SpotPrice" ] > self.data.at[ buy_index, "Price" ]:
                    # if comparison worth it just once, then we also want to continue to next hour 
                    # where we can potentially sell solar power
                    to_continue = True
                    #check if earlier buy_point than before. Use to get area to check for violations
                    if buy_index < first_buy_point:
                        first_buy_point = buy_index

                    # how much can be charged -> save to list or dict or smth like that.
                    # keep track of remaining
                    available_charge_max = self._get_charge_amount_available_maximum_at_index(
                                            dummy_df, buy_index )
                    available_charge_min = self._get_charge_amount_available_minimum_at_index(
                                            dummy_df, buy_index )

                    # find how much charge is needed not to go below or above limits!
                    # upper limit between charge and sell point, lower limit after sell point!
                    to_upper_limit = self._max_capacity - \
                                     self._get_battery_maximum_between_indices( dummy_df,
                                                                               buy_index,
                                                                               sell_index)

                    # need to make decisions depending on available charge vs remaining!
                    charge_amount = self._decide_charge_amount( available_charge_min, 
                                                                available_charge_max, 
                                                                to_upper_limit, 
                                                                remaining_necessary_charge )
                    if charge_amount > 0.0:
                        charge_success = self._set_charge_at_index( buy_index, 
                                                                    dummy_df, 
                                                                    charge_amount )
                        self._set_action_reason( dummy_df, buy_index, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                        if charge_success:
                            remaining_necessary_charge -= charge_amount
                    if remaining_necessary_charge <= 0.0:
                        # need to check validity - no breach of limits! 
                        # - checks from first buy point
                        violation = self._battery_check_if_above_maximum_charge( dummy_df, 
                                                                                 first_buy_point )
                        if violation[0] is None:
                            violation = self._battery_check_if_below_minimum_charge( dummy_df, 
                                                                                first_buy_point )
                        # need to save the changes to frame
                        if violation[0] is None:
                            result_frame = pd.DataFrame( dummy_df, copy=True )
                            save_result_to_output_frame = True
                        break
                else:
                    # if not worth to sell, i.e. comparison fails, then continue
                    break

            # enough? otherwise get available charging times after index and do the same
            # are there indexes after sell index?
            data_index_len = self.data.index.values.size
            if remaining_necessary_charge > 0.0 and data_index_len - 1 > sell_index:
                # get available charging times before index 
                charge_times_available = self.data.loc[ sell_index + 1 : data_index_len ] 
                # sort low to high
                charge_times_sorted = charge_times_available.sort_values( 'Price', ascending=True )
                for buy_index in charge_times_sorted.index.values:
                    # decide with comparison between sell vs buy price (spotprice vs price)
                    if self.data.at[ sell_index, "SpotPrice" ] > self.data.at[ buy_index, "Price" ]:
                    # if comparison worth it just once, then we also want to continue to next hour 
                    # where we can potentially sell solar power
                        to_continue = True

                        available_charge_max = self._get_charge_amount_available_maximum_at_index(
                                            dummy_df, buy_index )
                        available_charge_min = self._get_charge_amount_available_minimum_at_index(
                                            dummy_df, buy_index )
                        to_upper_limit = self._max_capacity - \
                                     self._get_battery_maximum_between_indices( dummy_df,
                                                                               buy_index,
                                                                               sell_index)

                        # need to make decisions depending on available charge vs remaining!
                        charge_amount = self._decide_charge_amount( available_charge_min, 
                                                                    available_charge_max, 
                                                                    to_upper_limit, 
                                                                    remaining_necessary_charge )
                        if charge_amount > 0.0:
                            charge_success = self._set_charge_at_index( buy_index, 
                                                                        dummy_df, 
                                                                        charge_amount )
                            self._set_action_reason( dummy_df, buy_index, 
                                        ActionReason.CHARGE_LATER_CONSUMPTION)
                            if charge_success:
                                remaining_necessary_charge -= charge_amount
                        if remaining_necessary_charge <= 0.0:
                            # need to check validity - no breach of limits! 
                            # - checks from first buy point
                            violation = self._battery_check_if_above_maximum_charge( dummy_df, 
                                                                                 first_buy_point )
                            if violation[0] is None:
                                violation = self._battery_check_if_below_minimum_charge( dummy_df, 
                                                                                 first_buy_point )
                            # need to save the changes to frame
                            if violation[0] is None:
                                result_frame = pd.DataFrame( dummy_df, copy=True )
                                save_result_to_output_frame = True
                                break
                                # if this loop is not run or in first for loop, the changes will not
                                # be saved! proceed to next sell point.

            # was price_index calculation positive -> otherwise break! - no need to fail every last
            # member of list
            if not to_continue:
                break

        if not save_result_to_output_frame:
            # print( "No solar was sold because of spotprice being higher than total price" )
            pass
        return result_frame
            

    def _solar_sell_timeframe_surplus( self, output_frame: pd.DataFrame ) -> None:
        """Sell the surplus solar power that is not needed in the day/timeframe."""
        # Find the solar charging points/times/indices
        #  ( surplus > 0 && equalize ) 
        # Not charge since then there is a need for the power and it has already been decided that
        # it is worthwhile to get the power in that timeslot.
        solar_charging_filter =  ( output_frame[ "SolarSurplus" ] > 0 ) & \
                                 ( output_frame[ "Action" ] == 'equalize' )
        solar_charging_sell_prices = self.data.loc[ solar_charging_filter ]
        # Sort by highest sell price
        solar_sell_prices_sorted = solar_charging_sell_prices.sort_values( 'SpotPrice', \
                                                                           ascending=False )
        # Loop the values
        end_index = output_frame.index.values.size - 1
        for sell_index in solar_sell_prices_sorted.index.values:
            # Find the minimum from sell point to the end. 
            to_bottom = self._max_charge_rate
            if sell_index < end_index:
                to_bottom = self._get_battery_minimum_between_indices( output_frame, 
                                                                    sell_index + 1,
                                                                    end_index ) - self._min_capacity
            # else: - Doesn't really matter what happens at the absolute end, by setting to_bottom
            # to 10, we sell at the end! Then we always sell, since we don't know what will happen
            # after.

            # Potentially make a check for index when bottom buffer is hit. If index earlier, then 
            #       continue!?!
            surplus_in_hour = output_frame.at[ sell_index, "BatteryDelta" ]
            # sell condition depends on setting

            if self._solar_strategy == SolarStrategy.SELL_ALL.value:
                sell_condition = True
            else:
                sell_condition = False

            # Sell if possible / change to idle
            if to_bottom >= surplus_in_hour and sell_condition:
                self._set_loadplan_action( output_frame, sell_index, 'idle' )
                self._set_action_reason( output_frame, sell_index, 
                                        ActionReason.IDLE_SOLAR_OVERFLOW )
    