""" 
Module for managing and testing the Planning module
Test regarding starting the adaptive model, where we can re-plan every hour.

Date:
    16-10-2023

"""

import pandas as pd

# from controller.planner import Planner
import controller.planner as pl


class Manager():
    """Manager class for handling logic on how to use planner to control MiniCon"""
    def __init__(self) -> None:
        # For testing:
        self.action_list = []#list() 
        self.combined_plan = pd.DataFrame()
    def test_planner( self, planner: pl.Planner, input_data: str, rt_consumption: str ) ->None: # -> list:
        """Function for testing planner with certain data!"""
        # action_list = []
        self.action_list.clear()
        input_frame = pd.read_csv( input_data )
        actual_consumption = pd.read_csv( rt_consumption )
        length_of_input = input_frame.index.values.size
        # set battery default value to smth else
        # pl.BATTERY_DEFAULT_START_LEVEL = 0.0
        planner.settings["battery_default_start_level"] = 0.0

        for iteration in range( length_of_input ) :
            print( f"iteration {iteration}, battery start level = {planner.settings['battery_default_start_level']}")
            # put shorter data frame
            shorter_frame = input_frame.loc[ iteration : length_of_input - 1 ]
            # create new indexes ! new df and indes list?
            new_indices = [*range( 0, length_of_input - iteration )]
            shorter_frame.index = new_indices
            # print( f"new index\n{new_indices}")
            planner._data = shorter_frame #pd.DataFrame( shorter_frame )
            # print(f"planner._data {planner._data}")
            
            # run planner
            planner.run_planner()
            # save the action to a list
            action = planner.plan.at[ 0, "Action" ]
            # action_list.append( action )
            self.action_list.append( action )

            # to add to combined plan
            to_append = planner.plan.loc[[0]]
            if iteration == 0:
                # start the dataframe
                self.combined_plan = pd.DataFrame( to_append, copy=True ) 
            else:
                #extend the frame
                self.combined_plan = pd.concat( [ self.combined_plan, to_append ], 
                                                ignore_index=True)
                

            if iteration < ( length_of_input - 1 ):
                # take into account the actual consumption to calculate the next battery default 
                expected_battery = planner.plan.at[ 1, "BatteryExpected" ]
                #"ActualConsumption" ] - \
                battery_delta = actual_consumption.at[ iteration, "ExpectedConsumption" ] - \
                                input_frame.at[ iteration, "ExpectedConsumption" ]
                # action = planner.plan.at[ 0, "Action" ]
                if action == 'equalize':
                    # not entirely correct, but close and simpler - keep numbers below max rate
                    new_bat_level = expected_battery - battery_delta
                    if new_bat_level > planner.settings["battery_capacity_minimum"]: #pl.BATTERY_CAPACITY_MINIMUM:
                        planner.settings["battery_default_start_level"] = new_bat_level
                    else:
                        planner.settings["battery_default_start_level"] = \
                                                    planner.settings["battery_capacity_minimum"]#0.0
                else:
                    # battery should be equal to battery expected!?!
                    planner.settings["battery_default_start_level"] = expected_battery

        # print(f"action_list =\n{self.action_list}")
       
        # return action_list

        #set default level back to zero !
        planner.settings["battery_default_start_level"] = 0.0
                

if __name__ == '__main__':
    print( "start manager main test")
    print("Create manager")
    manager = Manager()
    print("Create planner")
    test_planner = pl.Planner()

    print("Get test paths")
    testdata_path = "test_dataframe_1.csv"
    # testdata_path = "../../tests/controller/test_spotprice_high_feature.csv"
    testdata_frame = pd.read_csv( testdata_path )
    actual_path = "test_dataframe_1_actual_sim.csv"
    # actual_path = "test_dataframe_1.csv" # same actual as expected!
    actual_frame = pd.read_csv( actual_path )
    manager.test_planner( test_planner, testdata_path, actual_path )
    list_of_actions = manager.action_list#manager.test_planner( test_planner, testdata_frame, actual_frame )
    print( f"action_list: \n{list_of_actions}")

    overview_frame = pd.DataFrame( )
    overview_frame.insert( 0, "Adaptive", manager.action_list )
    

    # get what the planner does for the two separate lists
    print("Expected plan **********************************")
    test_planner._data = testdata_frame
    test_planner.run_planner()
    print( test_planner.plan[ ["Action", "BatteryExpected", "ActionReason"] ] )
    overview_frame.insert( 0, "ExpectedPlan", test_planner.plan[ "Action" ]) #

    print("Composite plan **********************************")
    print( manager.combined_plan[ ["Action", "BatteryExpected", "ActionReason"] ] )

    print("Plan for the 'actual data' **********************************")
    test_planner._data = actual_frame
    test_planner.run_planner()
    print( test_planner.plan[ ["Action", "BatteryExpected", "ActionReason"] ] )
    overview_frame.insert( 2, "'Actual'Plan", test_planner.plan[ "Action" ])
    
    print( f"overview_frame:\n {overview_frame}")

    # print( "the name of an action ")
    # print( pl.ActionReasons.NONE.name )
    # print( f"get description: {pl.ActionReasons.get_description(name='NONE')}")

    overview_frame.to_csv( 'adaptive_test.csv' )