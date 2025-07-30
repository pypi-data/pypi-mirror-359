"""
This code has been written by stephane.ploix@grenoble-inp.fr
It is protected under GNU General Public License v3.0
"""
import enum
import datetime
from typing import Any


class WEEKDAYS(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class SignalCapper:
    """
    This class is a setpoint generator. It first generates a constant setpoint and proposes different
    methods to intersect with the original signal. The value None means no setpoint i.e. control
    is off.
    """

    def __init__(self, datetimes: list[datetime.datetime], base_values: float | list[float]):
        """
        Initialize the setpoint generator.

        :param reference_setpoint: the constant maximum setpoint value
        :type reference_setpoint: float
        :param datetimes: the list of dates (hours) corresponding to samples (that should be identical to
        to a Data object for integration)
        :type datetimes: list[datetime]
        """
        self.datetimes: list[datetime.datetime] = datetimes
        if type(base_values) is float:
            self.base_value: float = base_values
            self._values: list[float] = [base_values for _ in range(len(datetimes))]
        else:
            self._values = base_values

    def __call__(self) -> list[float]:
        """
        Return the setpoint values

        :return: setpoint values
        :rtype: list[float]
        """
        return self._values

    def _min(self, values: list[float]) -> list[float]:
        """
        Internal method used to intersect (take the minimum of the current setpoints and the provided ones)
        another list of setpoints

        :param setpoints: setpoints that will be compared to the current setpoint values: the minimum is
        computed for each sample and replace the current setpoint value. None is the minimum of all the possible values
        :type setpoints: list[float]
        """
        for i in range(len(self.datetimes)):
            if values[i] is not None:
                self._values[i] = min(self._values[i], values[i])

    def subtract(self, values: list[float]) -> None:
        for i in range(len(self.datetimes)):
            self._values[i] = self._values[i] - values[i]

    def add(self, values: list[float]) -> None:
        for i in range(len(self.datetimes)):
            self._values[i] = self._values[i] + values[i]

    def multiply(self, values: list[float]) -> None:
        for i in range(len(self.datetimes)):
            self._values[i] = self._values[i] * values[i]

    def period(self, period_start: tuple[int, int] = (15, 3), period_end: tuple[int, int] = (15, 10), in_between: bool = True) -> None:
        """
        Generate setpoints corresponding to seasonal start and stop of the HVAC system for instance.

        :param summer_period_start: starting date for the summer period (signal starts to be off), defaults to '15/03'
        :type summer_period_start: str, optional
        :param summer_period_end: ending date for the summer period (end of the off values), defaults to '15/10'
        :type summer_period_end: str, optional
        """
        values = list()
        for _datetime in self.datetimes:
            start_day, end_day = period_start[0], period_end[0]
            start_month, end_month = period_start[1], period_end[1]

            in_period = None
            if start_month < _datetime.month < end_month:
                in_period: bool = True
            elif (start_month == _datetime.month and _datetime.day >= start_day) and (end_month == _datetime.month and _datetime.day < end_day):
                in_period = True
            else:
                in_period = False
            if in_period:
                if in_between:
                    values.append(0)
                else:
                    values.append(None)
            else:
                if in_between:
                    values.append(None)
                else:
                    values.append(0)
        self._min(values)

    def daily(self, weekdays: list[int], value: float, hour_triggers: list[int], initial_on_state: bool = True):
        """
        Generate a setpoint corresponding to daily hours for selected days of the week.

        :param weekdays: list of the days of the week (0: Monday,... 6: Sunday) concerned by the setpoints
        :type weekdays: list[int]
        :param low_setpoint: low setpoint values used for computing the intersection with the current signal
        :type low_setpoint: float
        :param triggers: hours where the signal will switch from reference setpoint value to the low setpoint
        value and conversely, defaults to list[int]
        :type triggers: list[int], optional
        :param initial_on_state: initial setpoint value is low setpoint if False and reference setpoint value if True, defaults to False
        :type initial_on_state: bool, optional

        """
        current_state: bool = initial_on_state
        hour_triggers: list[int] = sorted(hour_triggers)
        on_triggers: dict[int, bool] = dict()
        for trigger in hour_triggers:
            on_triggers[trigger] = not current_state
            current_state = not current_state

        if type(weekdays) is int:
            weekdays: list[int] = [weekdays]
        setpoints: list[float] = list()
        profile: list[float] = list()
        on_state: bool = False
        for trigger_index in range(hour_triggers[0]):
            profile.append(self.base_value if not hour_triggers[0] else value)
        for trigger_index in on_triggers:
            while len(profile) < trigger_index:
                if on_state:
                    profile.append(self.base_value)
                else:
                    profile.append(value)
            on_state = on_triggers[trigger_index]
        for _ in range(trigger_index, 24):
            profile.append(self.base_value if on_triggers[trigger_index] else value)

        for _datetime in self.datetimes:
            if _datetime.weekday() in weekdays:
                setpoints.append(profile[_datetime.hour])
            else:
                setpoints.append(None)
        self._min(setpoints)

    def long_absence(self, number_of_days: int, presence: list[float]):
        """
        Detect long absences for setting the setpoints to 0.

        :param long_absence_setpoint: setpoint value in case of long absence detected
        :type long_absence_setpoint: float
        :param number_of_days: number of days over which a long absence is detected
        :type number_of_days: int
        :param presence: list of hours with presence (>0) and absence (=0)
        :type presence: list[float]
        """
        long_absence_start: int = None  # starting index for long absence
        long_absence_counter: int = 0
        values: list = list()
        for i in range(len(self.datetimes)):
            if presence[i] > 0:  # presence
                if long_absence_start is not None:  # long absence detected and ongoing
                    if long_absence_start + long_absence_counter > number_of_days * 24:  # long absence detected but is over (presence detected)
                        for i in range(long_absence_start, long_absence_counter):  # add long absence.endswith() setpoints
                            values.append(None)  # long_absence_value
                    else:  # long absence has not been detected
                        for i in range(long_absence_start, long_absence_counter):
                            values.append(0)
                    values.append(0)
                long_absence_counter = 0  # reinitialize the long absence counter
            else:  # absence
                if long_absence_start is None:  # first absence detection
                    long_absence_counter = 1
                    long_absence_start = i
                else:  # new absence detection
                    long_absence_counter += 1
        for i in range(len(values), len(self.datetimes)):
            values.append(None)
        self._min(values)

    def capping(self, capping_values: float, threshold: float, thresholding_values: list[float] = None, opposite: bool = False):
        """
        Modify setpoint values on the occurrence of setpoint (window opening ratio for instance) values of an extra-signal passing a threshold.

        :param opening_setpoint: setpoint value to be used in case of the extra signal pass a threshold
        :type opening_setpoint: list[float]
        :param opening_threshold: threshold over which the opening threshold value will be applied.
        :type opening_threshold: float
        :param openings: extra-signal whose values will trigger the right setpoint
        :type openings: list[float]
        """
        values: list = list()
        if thresholding_values is None:
            thresholding_values: list[float] = capping_values
        for i in range(len(self.datetimes)):
            if not opposite:
                values.append(capping_values if thresholding_values[i] >= threshold else self.base_value)
            else:
                values.append(None if thresholding_values[i] >= threshold else capping_values)
        self._min(values)


class DaySignalMaker:

    def __init__(self, datetimes: list[datetime.datetime], night_value: float = 0, integer: bool = False, default_hour_values: tuple[float, float] = ()) -> None:
        self.integer: bool = integer
        self.night_value: float = night_value
        self.datetimes: list[datetimes.datetimes] = datetimes
        if len(default_hour_values) == 0:
            self.default_day_profile = [night_value for _ in range(len(datetimes))]
        else:
            self.default_day_profile: list[float] = self.__expand(default_hour_values)
        self.day_profiles: dict[int, list[float]] = dict()

    def add_day_of_week_profile(self, days_of_week: tuple[int], hour_values: tuple[float, float]) -> None:
        profile: list[float] = self.__expand(hour_values)
        for d in days_of_week:
            self.day_profiles[d] = profile

    def __expand(self, hour_value_marks: tuple[tuple[float, float]]) -> list[float]:
        if len(hour_value_marks) == 0:
            day_values: list[float] = [self.night_value for _ in range(len(self.datetimes))]
        else:
            day_values = list()
            hour_value_marks = list(hour_value_marks)
            hour_value_marks.sort(key=lambda mark: mark[0])
            if hour_value_marks[0][0] < 0:
                raise "Error: hour in day can't be negative"
            if hour_value_marks[-1][0] >= 24:
                raise "Error: hour in day can't be greater or equal to 24"
            if hour_value_marks[0][0] > 0:
                hour_value_marks.insert(0, (hour_value_marks[0][0], self.night_value))
                hour_value_marks.insert(0, (0, self.night_value))
                hour_value_marks.append((hour_value_marks[-1][0], self.night_value))
                hour_value_marks.append((24, self.night_value))
            i = 0
            for day_hour in range(24):
                while not (hour_value_marks[i][0] <= day_hour <= hour_value_marks[i+1][0]):
                    i += 1
                if hour_value_marks[i][0] == hour_value_marks[i+1][0]:
                    value = (hour_value_marks[i][0] + hour_value_marks[i+1][0])/2
                    if self.integer:
                        value = round(value)
                    day_values.append(value)
                else:
                    value: float = DaySignalMaker.__interpolate(day_hour, hour_value_marks[i][0], hour_value_marks[i+1][0], hour_value_marks[i][1], hour_value_marks[i+1][1])
                    if self.integer:
                        value = round(value)
                    day_values.append(value)
        return day_values

    @staticmethod
    def __interpolate(time: int, previous_time: int, next_time: int, previous_value: float, next_value: float) -> float:
        return previous_value + (next_value - previous_value) * (time - previous_time) / (next_time - previous_time)

    def __call__(self) -> list[int] | list[float]:
        """generate a uniform random sequence of integer of float values
        :return: the random sequence
        :rtype: list[int]|list[float]
        """
        _value_sequence = list()
        for dt in self.datetimes:
            day_of_week: int = dt.weekday()
            hour_in_day: int = dt.hour
            if day_of_week in self.day_profiles:
                _value_sequence.append(self.day_profiles[day_of_week][hour_in_day])
            else:
                _value_sequence.append(self.default_day_profile[hour_in_day])

        return _value_sequence


class SignalGenerator:

    def __init__(self, datetimes: list[datetime.datetime]):
        self.datetimes: list[datetime.datetime] = datetimes
        self.starting_datetime: datetime.datetime = datetimes[0]
        self.starting_year: int = self.starting_datetime.year
        self.starting_month: int = self.starting_datetime.month
        self.starting_day: int = self.starting_datetime.day
        self.ending_datetime: datetime.datetime = datetimes[-1]
        self.ending_year: int = self.ending_datetime.year
        self.ending_month: int = self.ending_datetime.month
        self.ending_day: int = self.ending_datetime.day
        
    def __call__(self, value: float | None) -> list[float | None]:
        return [value for _ in range(len(self.datetimes))]
        
    def combine(self, signal1: list[float | None] | float, signal2: list[float | None] | float, operator: callable,  none_dominate: bool = False) -> Any:
        if signal1 is None and signal2 is None:
            return None
        elif signal1 is None and type(signal2) is float:
            if none_dominate:
                return None
            else:
                return signal2
        elif signal2 is None and type(signal1) is float:
            if none_dominate:
                return None
            else:
                return signal1
        elif type(signal1) is float and type(signal2) is float:
            return operator(signal1, signal2)
        elif type(signal1) is float and type(signal2) is list[float | None]:
            signal1 = [signal1 for _ in range(len(signal2))]
        elif type(signal2) is float and type(signal1) is list[float | None]:
            signal2 = [signal2 for _ in range(len(signal1))]

        signal: list[float | None] = list(signal1)
        for k in range(len(signal1)):
            if signal1[k] is None and signal2[k] is None:
                signal[k] = None
            elif signal1[k] is None:
                if none_dominate:
                    signal[k] = None
                else:
                    signal[k] = signal2[k]
            elif signal2[k] is None:
                if none_dominate:
                    signal[k] = None
            else:
                signal[k] = operator(signal1[k], signal2[k])
        return signal

    def constant(self, signal: list[float | None], constant: float) -> list[float | None]:
        """
        Add a constant value to a signal.
        
        :param signal: input signal
        :param constant: constant value to add
        :return: signal with constant added
        """
        return self.combine(signal, constant, lambda x, y: x + y)

    def seasonal(self, day_month_start: str, day_month_end: str, seasonal_value: float = 1, out_season_value: float = None,
                 period2_start: str = None, period2_end: str = None, period2_value: float = None) -> list[float | None]:
        """
        Generate a seasonal signal with one or two periods per year.
        
        :param day_month_start: start date of first period in format 'DD/MM'
        :param day_month_end: end date of first period in format 'DD/MM'
        :param seasonal_value: value during the first period
        :param out_season_value: value outside the first period (or between periods if second period is specified)
        :param period2_start: start date of second period in format 'DD/MM' (optional)
        :param period2_end: end date of second period in format 'DD/MM' (optional)
        :param period2_value: value during the second period (optional)
        :return: seasonal signal
        """
        year = self.starting_year
        
        # Parse dates for first period
        day1, month1 = tuple([int(v) for v in day_month_start.split('/')])
        day2, month2 = tuple([int(v) for v in day_month_end.split('/')])
        
        # Create datetime thresholds for first period
        period1_start_dt = datetime.datetime(
            year=year, month=month1, day=day1,
            hour=0, minute=0, second=0, microsecond=0,
            tzinfo=self.starting_datetime.tzinfo
        )
        period1_end_dt = datetime.datetime(
            year=year, month=month2, day=day2,
            hour=0, minute=0, second=0, microsecond=0,
            tzinfo=self.starting_datetime.tzinfo
        )
        
        # Handle year transitions for first period
        if period1_end_dt < period1_start_dt:
            period1_end_dt = period1_end_dt.replace(year=year+1)
        
        # Check if second period is specified
        has_second_period = period2_start is not None and period2_end is not None and period2_value is not None
        
        if has_second_period:
            # Parse dates for second period
            day2_start, month2_start = tuple([int(v) for v in period2_start.split('/')])
            day2_end, month2_end = tuple([int(v) for v in period2_end.split('/')])
            
            # Create datetime thresholds for second period
            period2_start_dt = datetime.datetime(
                year=year, month=month2_start, day=day2_start,
                hour=0, minute=0, second=0, microsecond=0,
                tzinfo=self.starting_datetime.tzinfo
            )
            period2_end_dt = datetime.datetime(
                year=year, month=month2_end, day=day2_end,
                hour=0, minute=0, second=0, microsecond=0,
                tzinfo=self.starting_datetime.tzinfo
            )
            
            # Handle year transitions for second period
            if period2_end_dt < period2_start_dt:
                period2_end_dt = period2_end_dt.replace(year=year+1)
        
        signal = list()
        for dt in self.datetimes:
            # Check if current datetime is in first period
            in_period1 = self._is_in_period(dt, period1_start_dt, period1_end_dt, year)
            
            if has_second_period:
                # Check if current datetime is in second period
                in_period2 = self._is_in_period(dt, period2_start_dt, period2_end_dt, year)
                
                # Determine the value based on which period the datetime falls into
                if in_period1:
                    signal.append(seasonal_value)
                elif in_period2:
                    signal.append(period2_value)
                else:
                    signal.append(out_season_value)
            else:
                # Original single period logic
                if in_period1:
                    signal.append(seasonal_value)
                else:
                    signal.append(out_season_value)
        
        return signal
    
    def _is_in_period(self, dt: datetime.datetime, period_start: datetime.datetime, period_end: datetime.datetime, base_year: int) -> bool:
        """
        Helper method to check if a datetime falls within a period.
        
        :param dt: datetime to check
        :param period_start: start of the period
        :param period_end: end of the period
        :param base_year: base year for the period
        :return: True if datetime is in period, False otherwise
        """
        # Adjust period dates to match the year of the datetime being checked
        dt_year = dt.year
        
        adjusted_start = period_start.replace(year=dt_year)
        adjusted_end = period_end.replace(year=dt_year)
        
        # Handle periods that cross year boundary
        if adjusted_end < adjusted_start:
            # Period crosses year boundary
            if dt >= adjusted_start or dt < adjusted_end:
                return True
        else:
            # Period is within the same year
            if adjusted_start <= dt < adjusted_end:
                return True
        
        return False

    def daily(self, info_signal: list[float | None], trigger_value: float, weekdays: list[WEEKDAYS], hour_setpoints: dict[int, float]) -> list[float | None]:
        """
        Generate a daily signal based on weekdays and hour setpoints.
        
        :param signal: input signal to modify (can be None for new signal)
        :param weekdays: list of weekdays to apply the schedule
        :param hour_setpoints: dictionary mapping hours to setpoint values
        :return: modified signal with daily schedule applied
        """
        # Convert WEEKDAYS enum to integers for comparison
        weekday_ints = [d.value if hasattr(d, 'value') else d for d in weekdays]
        
        # Build the 24-hour day sequence
        previous_hour, previous_setpoint = None, None
        day_sequence = list()
        
        if 0 not in hour_setpoints:
            raise ValueError("0 must appear in the trigger dictionary")
            
        # Sort hours to ensure they are in increasing order
        sorted_hours = sorted(hour_setpoints.keys())
        
        for hour in sorted_hours:
            if previous_hour is None:
                previous_hour, previous_setpoint = hour, hour_setpoints[hour]
            else:
                # Fill the gap between previous hour and current hour
                for _ in range(previous_hour, hour):
                    day_sequence.append(previous_setpoint)
                previous_hour, previous_setpoint = hour, hour_setpoints[hour]
        
        # Fill the remaining hours until 24
        for hour in range(previous_hour, 24):
            day_sequence.append(previous_setpoint)
            
        # Create or modify the signal
        signal = [None] * len(self.datetimes)
            
        for i, dt in enumerate(self.datetimes):
            if dt.weekday() in weekday_ints:
                if info_signal[i] == trigger_value:
                    signal[i] = day_sequence[dt.hour]
            # else:
            #     info_signal[i] = None
            # If not in specified weekdays, keep the original value (None or existing)
            
        return signal

    def long_absence(self, high_setpoint: float, long_absence_setpoint: float, number_of_days: int, presence: list[float]) -> list[float]:
        long_absence_start = None  # starting index for long absence
        long_absence_counter: int = 0
        signal: list = list()
        for i in range(len(self.datetimes)):
            if presence[i] > 0:  # presence
                if long_absence_start is not None:  # long absence detected and ongoing
                    if long_absence_start + long_absence_counter > number_of_days * 24:  # long absence detected but is over (presence detected)
                        for i in range(long_absence_start, long_absence_counter):  # add long absence.endswith() setpoints
                            signal.append(long_absence_setpoint)
                    else:  # long absence has not been detected
                        for i in range(long_absence_start, long_absence_counter):
                            signal.append(high_setpoint)
                    signal.append(high_setpoint)
                long_absence_counter = 0  # reinitialize the long absence counter
            else:  # absence
                if long_absence_start is None:  # first absence detection
                    long_absence_counter = 1
                    long_absence_start = i
                else:  # new absence detection
                    long_absence_counter += 1
        for i in range(len(signal), len(self.datetimes)):
            signal.append(high_setpoint)
        return signal

    def cap(self, signal: list[float | None], capped_value: float, threshold: float, capping_signal: list[float | None] = None) -> list[float | None]:
        if capping_signal is None:
            capping_signal = signal
        for i in range(len(self.datetimes)):
            if capping_signal[i] is not None:
                if capping_signal[i] > threshold:
                    signal[i] = capped_value
        return signal

    def cup(self, signal: list[float], cupped_value: float, threshold: float, cupping_signal: list[float] = None) -> None:
        if cupping_signal is None:
            cupping_signal = self.signal
        for i in range(len(self.datetimes)):
            if cupping_signal[i] is not None:
                if cupping_signal[i] < threshold:
                    signal[i] = cupped_value
        return signal

    def amplify(self, signal: list[float | None], alpha: float) -> list[float | None]:
        for k in range(len(self.datetimes)):
            if signal[k] is not None:
                signal[k] = signal[k] * alpha
        return signal
    
    def replace(self, signal: list[float | None], value: float, replacement_value: float) -> list[float | None]:
        for k in range(len(self.datetimes)):
            if signal[k] == value:
                signal[k] = replacement_value
        return signal

    def integerize(self, signal: list[float | None], none_value: int = 0) -> list[float | None]:
        for k in range(len(self.datetimes)):
            if signal[k] is None:
                signal[k] = none_value
        return signal


class ModeSetpointSiggen:

    def __init__(self, datetimes: list[datetime.datetime], heating_period: tuple[str, str] = ('15/10', '15/4'), cooling_period: tuple[str, str] = ('15/6', '15/9'), default_setpoints: bool = False) -> None:
        self.has_heating: bool = heating_period is not None
        self.has_cooling: bool = cooling_period is not None
        self.siggen = SignalGenerator(datetimes)
        self.modes: list[float | None] = self.siggen(0)
        self.temperature_setpoints: list[float | None] = self.siggen(None)
        # day_month_start: str, day_month_end: str, seasonal_value: float = 1, out_season_value: float = None
        if self.has_heating:
            self.heating_modes = self.siggen.seasonal(*heating_period, seasonal_value=1, out_season_value=None)
            self.modes = self.siggen.combine(self.modes, self.heating_modes, lambda x, y: x + y)
        if self.has_cooling:
            self.cooling_modes = self.siggen.seasonal(*cooling_period, seasonal_value=1, out_season_value=None)
            self.modes = self.siggen.combine(self.modes, self.cooling_modes, lambda x, y: x - y)
        if default_setpoints:
            self.temperature_setpoints = self.siggen.combine(self.temperature_setpoints, self.add_daily_setpoints(self.modes, 1, [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: None, 6: 21, 18: None}), lambda x, y: x + y)
            self.temperature_setpoints = self.siggen.combine(self.temperature_setpoints, self.add_daily_setpoints(self.modes, -1, [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], {0: None, 6: 24, 18: None}), lambda x, y: x + y)
            
    def add_daily_setpoints(self, mode_signal: list[float | None], trigger_value: int, days_of_week: list[WEEKDAYS], hour_setpoints: dict[int, float]) -> None:
        weekdays_int: list[WEEKDAYS | int] = [d.value if hasattr(d, 'value') else d for d in days_of_week]
        setpoint_signal: list[float | None] = self.siggen.daily(mode_signal, trigger_value, weekdays_int, hour_setpoints)
        # signal = self.siggen.replace(signal, 0, None)
        self.temperature_setpoints = self.siggen.combine(self.temperature_setpoints, setpoint_signal, lambda x, y: x + y)
        pass

    # def add_cooling_daily_setpoints(self, days_of_week: list[int] = [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], hour_setpoints: dict[int, float] = {0: None, 6: 24, 18: None}):
    #     # Convert WEEKDAYS enum objects to integers if needed
    #     weekdays_int = [d.value if hasattr(d, 'value') else d for d in days_of_week]
    #     signal: list[float | None] = self.siggen.daily(self.heating_modes, -1,weekdays_int, hour_setpoints)
    #     # signal = self.siggen.replace(signal, 0, None)
    #     self.temperature_setpoints = self.siggen.combine(self.temperature_setpoints, signal, lambda x, y: x + y)

    def get_modes(self) -> list[float]:
        # if self.has_heating and not self.has_cooling:
        #     temperature_setpoints: list[float] = self.heating_modes_sgen()
        # elif not self.has_heating and self.has_cooling:
        #     temperature_setpoints: list[float] = self.cooling_modes_sgen()
        # elif self.has_heating and self.has_cooling:
        #     temperature_setpoints: list[float] = self.siggen.combine(self.heating_modes, self.cooling_modes, lambda x, y: x - y)
        return self.modes
    
    def get_setpoints(self) -> tuple[list[float], list[float]]:
        # if self.has_heating and not self.has_cooling:
        #     temperature_setpoints: list[float] = self.heating_modes_sgen()
        # elif not self.has_heating and self.has_cooling:
        #     temperature_setpoints: list[float] = self.cooling_modes_sgen()
        # elif self.has_heating and self.has_cooling:
        #     temperature_setpoints: list[float] = self.siggen.combine(self.heating_modes, self.cooling_modes, lambda x, y: x - y)
        return self.temperature_setpoints


class HeaterModeSetpointSiggen(ModeSetpointSiggen):
    def __init__(self, datetimes: list[datetime.datetime], heating_period: tuple[str, str] = ('15/10', '15/4'), days_of_week: list[int] = [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], hour_setpoints: dict[int, float] = {0: None, 6: 21, 18: None}) -> None:
        super().__init__(datetimes, heating_period, None)
        # Convert WEEKDAYS enum objects to integers if needed
        weekdays_int = [d.value if hasattr(d, 'value') else d for d in days_of_week]
        self.add_daily_setpoints(weekdays_int, hour_setpoints)


class CoolerModeSetpointSiggen(ModeSetpointSiggen):
    def __init__(self, datetimes: list[datetime.datetime], cooling_period: tuple[str, str] = ('15/6', '15/9'), days_of_week: list[int] = [WEEKDAYS.MONDAY, WEEKDAYS.TUESDAY, WEEKDAYS.WEDNESDAY, WEEKDAYS.THURSDAY, WEEKDAYS.FRIDAY], hour_setpoints: dict[int, float] = {0: None, 6: 24, 18: None}) -> None:
        super().__init__(datetimes, None, cooling_period)
        # Convert WEEKDAYS enum objects to integers if needed
        weekdays_int = [d.value if hasattr(d, 'value') else d for d in days_of_week]
        self.add_cooling_daily_setpoints(weekdays_int, hour_setpoints)