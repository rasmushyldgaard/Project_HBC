"""
Asynchronous scheduling of background tasks for GUI

Date:
    30-10-2023

"""

import pandas as pd

from typing import Any
from copy import deepcopy
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future

from data import get_battery, Battery
from controller import Planner, ActionReason
from database import Database


# Max Capacity (cap), BatteryExpected (exp)
expected_soc = lambda cap, exp : round((exp * 100 / cap), 4)   # TODO: Make sure Application
                                                               #       can't set cap to 0 

class Scheduler:
    """ Class for scheduling tasks in application """
    def __init__(self, app: Any, settings: dict[str, Any]):
        self._app = app
        self._settings = self._transform_settings(settings)
        self._planner = Planner(self._settings)
        self._plan_index = 0
        # self._load_plan_and_data() TODO: Fix this so it loads entire plan and data!
        self._battery: Battery = self._planner.battery
        self._expected_soc = expected_soc(self._settings['capacity'], self._planner.plan.at[1, "BatteryExpected"])
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._tasks = {
            'planner': {
                'next_schedule': datetime.now(),
                'scheduled': False,
                'waiting': False,
                'future': Future(),
            },

            'monitor': {
                'next_schedule': datetime.now(),
                'scheduled': False,
                'waiting': False,
                'future': Future(),
            },
        }
    
    @property
    def plan(self) -> pd.DataFrame:
        """ Get generated plan from Planner """
        return self._planner.plan
    
    @property
    def data(self) -> pd.DataFrame:
        """ Get the input data to Planner """
        return self._planner.data
    
    @property
    def battery(self) -> Battery:
        """ Get the battery information """
        return self._battery


    def clock_it(self, current_time: datetime) -> None:
        """ Scheduler "clocks" itself every 10s to check for scheduling and running tasks

        Args:
            current_time: Current day and time
        
        """
        next_action_time = self.plan.at[self._plan_index, 'Time'].to_pydatetime()
        next_planner_time = next_action_time - timedelta(minutes=2)                 # XX:58:00
        next_monitor_time = current_time + timedelta(minutes=1)                     # XX:01:XX
        self._scheduling(current_time, next_planner_time, next_monitor_time)
        self._update_tasks(current_time)
        self._fetch_results()

        if current_time >= next_action_time:
            if not self._tasks['monitor']['future'].running(): # type: ignore
                # set_battery(self.plan.at[self._plan_index, 'Action'])
                self._app.update_ui()
                self._plan_index = 1
            

    def update_settings(self, settings: dict[str, str]) -> None:
        """ Update settings attribute in Scheduler object\n
        This method should only be called from the "Apply" button callback in ProfileTab!

        Args:
            settings: Saved user settings from Application

        """
        self._settings = self._transform_settings(settings)


    def shutdown(self) -> None:
        """ Shutdown of ThreadPoolExecutor attribute in Scheduler object """
        self._executor.shutdown(wait=False, cancel_futures=True)


    def _scheduling(self, current_time: datetime,
                    next_planner_time: datetime, next_monitor_time: datetime) -> None:
        """ Scheduling of tasks based on current timing 
        
        Args:
            current_time: Current day and time
            next_planner_time: Next time to run Planner task
            next_monitor_time: Next time to run Monitor task

        """
        if not self._tasks['planner']['scheduled']:
            if next_planner_time > current_time:
                self._tasks['planner']['next_schedule'] = next_planner_time
                self._tasks['planner']['scheduled'] = True
                
        if not self._tasks['monitor']['scheduled']:
            self._tasks['monitor']['next_schedule'] = next_monitor_time
            self._tasks['monitor']['scheduled'] = True


    def _update_tasks(self, current_time: datetime) -> None:
        """ Update and run tasks based on their scheduled timings
        
        Args:
            current_time: Current day and time
            next_action_time: Next time to take an action

        """
        if not self._tasks['planner']['future'].running() and self._tasks['planner']['scheduled']: # type: ignore
            if current_time >= self._tasks['planner']['next_schedule']:                            # type: ignore
                self._tasks['planner']['future'] = self._executor.submit(self._task_planner,
                                                                         self._settings)
                self._tasks['planner']['scheduled'] = False
                self._tasks['planner']['waiting'] = True

        # Check if Planner task is running since it has higher priority
        if not self._tasks['planner']['future'].running() and self._tasks['monitor']['scheduled']: # type: ignore
            if current_time >= self._tasks['monitor']['next_schedule']:                            # type: ignore
                self._tasks['monitor']['future'] = self._executor.submit(self._task_battery_monitor)
                self._tasks['monitor']['scheduled'] = False
                self._tasks['monitor']['waiting'] = True


    def _fetch_results(self) -> None:
        """ Fetches the results from finished tasks """
        if self._tasks['planner']['waiting']:
            if self._tasks['planner']['future'].done(): # type: ignore
                self._planner = self._tasks['planner']['future'].result() # type: ignore
                self._tasks['planner']['waiting'] = False
                
        if self._tasks['monitor']['waiting']:
            if self._tasks['monitor']['future'].done(): # type: ignore
                self._battery = self._tasks['monitor']['future'].result() # type: ignore

                if self._battery.soc >= self._expected_soc:
                    # set_battery("idle")
                    self._app.update_ui("idle", ActionReason.IDLE.value, section="action")
                
                self._app.update_ui(section="battery")    
                self._tasks['monitor']['waiting'] = False


    def _save_plan_and_data(self) -> None:  # TODO: Fix this so it saves entire plan and data!
        """ Save current Planner plan and data in database incase of unexpected shutdown """
        db = Database()
        current_plan = self._planner.plan.loc[0].to_list()
        current_plan.extend(self._planner.data.loc[0].to_list()[1:])
        current_plan[0] = datetime.strftime(current_plan[0].to_pydatetime(), "%Y-%m-%d, %H:%M:%S")

        if db.check_for_empty_table('plan'):
            db.insert_into_table('plan', tuple(current_plan))
        else:
            db.update_table('plan', tuple(current_plan))


    def _load_plan_and_data(self) -> None: # TODO: Fix this so it loads entire plan and data!
        """ Check if there is a relevant saved plan in database and load into application """
        db = Database()
        next_action_time = self.plan.at[0, 'Time'].to_pydatetime()
        last_action_time = next_action_time - timedelta(1)

        # Check that a plan exists in Database
        if not db.check_for_empty_table('plan'):
            content = db.load_plan()
            saved_time = datetime.strptime(content['Time'], "%Y-%m-%d, %H:%M:%S")

            # Check if the time for the saved plan is still relevant
            if saved_time > last_action_time and saved_time < next_action_time: # pylint: disable=chained-comparison
                content_values = list(content.values())
                columns = list(content.keys())

                # Insert saved rows into plan and data
                plan = pd.Series([saved_time, *content_values[1:len(self._planner.plan.columns)]],
                                 index=columns[:len(self._planner.plan.columns)])
                data = pd.Series([saved_time, *content_values[len(self._planner.plan.columns):]],
                                 index=[columns[0], *columns[len(self._planner.plan.columns):]])
                self._planner.plan.loc[0] = plan    # type: ignore
                self._planner.data.loc[0] = data    # type: ignore
                self._planner.plan.sort_index(inplace=True)
                self._planner.data.sort_index(inplace=True)


    def _task_planner(self, settings: dict[str, Any]) -> Planner:
        """ Task for running the Planner and generate a new Planner object 
        
        Args:
            settings: User settings from Application

        Returns:
            A Planner object with generated plan
        
        """
        return Planner(settings)


    def _task_battery_monitor(self) -> Battery:
        """ Task for monitoring battery system and generate a new Battery object

        Returns:
            A Battery object with SoC and Real Consumption
         
        """
        return get_battery()


    def _transform_settings(self, settings: dict) -> dict[str, Any]: # type: ignore
        """ Transforms settings from strings to their native Python types

        Args:
            settings: User settings from Application

        Returns:
            Transformed settings with str keys and native Python values
         
        """
        transformed_settings = deepcopy(settings)
        transformed_settings['solcast_ids'] = transformed_settings['solcast_ids'].split(',')
        transformed_settings['capacity'] = int(transformed_settings['capacity'])
        transformed_settings['effectivity'] = float(transformed_settings['effectivity']) / 100
        transformed_settings['threshold'] = float(transformed_settings['threshold']) / 100
        transformed_settings['max_rate'] = int(transformed_settings['max_rate'])

        return transformed_settings

    
    