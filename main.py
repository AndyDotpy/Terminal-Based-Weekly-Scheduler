from datetime import datetime, date
import pytz
from typing import Final, Callable, Any
import os
import pickle
import sys
from copy import deepcopy


class Days:
    MONDAY: Final[int] = 0
    TUESDAY: Final[int] = 1
    WEDNESDAY: Final[int] = 2
    THURSDAY: Final[int] = 3
    FRIDAY: Final[int] = 4
    SATURDAY: Final[int] = 5
    SUNDAY: Final[int] = 6
    TODAY: Final[int] = 7

    __DAY_STRS: dict[int, str] = {
        MONDAY: "Monday",
        TUESDAY: "Tuesday",
        WEDNESDAY: "Wednesday",
        THURSDAY: "Thursday",
        FRIDAY: "Friday",
        SATURDAY: "Saturday",
        SUNDAY: "Sunday",
        TODAY: "Today"
    }

    @staticmethod
    def valid_day(day: int | None) -> bool:
        if day is None or day < 0 or day > 7:
            print("Provide an integer that is in range 0 - 7 inclusive")
            return False
        return True

    @staticmethod
    def get_str(day: int) -> str:
        return Days.__DAY_STRS.get(day, f"Day {day} is not between 0 - 7 inclusive")


class Task:
    def __init__(self, name: str, description: str, hour_start: int, fifteens_into_hour: int, duration_in_fifteens: int):
        self.name = name
        self.description = description
        self.hour_start = hour_start
        self.fifteens_into_hour = fifteens_into_hour
        self.duration_in_fifteens = duration_in_fifteens

    @staticmethod
    def add_zero(num: int) -> str:
        return_str = str(num)
        return "0" + return_str if len(return_str) == 1 else return_str

    def __str__(self) -> str:
        end_time_in_fifteens: int = self.hour_start * 4 + self.fifteens_into_hour + self.duration_in_fifteens
        hour_end: int = end_time_in_fifteens // 4
        fifteens_end: int = end_time_in_fifteens % 4
        return_str: str = (
            f"{self.name} from {Task.add_zero(self.hour_start)}:{Task.add_zero(self.fifteens_into_hour * 15)} - "
            f"{Task.add_zero(hour_end)}:{Task.add_zero(fifteens_end * 15)}"
        )
        if self.description:
            return_str += "\nDescription: " + self.description
        return return_str + "\n----- ----- ----- ##### ----- ----- -----"

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(self.name + self.description + str(self.hour_start) + str(self.fifteens_into_hour) + str(self.duration_in_fifteens))


timeline_length: int = 96  # Number of 15 minute segments in a day
timeline: list[Task | None] = [None] * timeline_length
cls_msg = "cls" if os.name == "nt" else "clear"
FILE_NAME: str = "schedules.pkl"
current_day: datetime = datetime.now(pytz.timezone("US/Eastern"))
date_opened: date = current_day.date()

schedules: dict[int, set[Task]] = {
    Days.MONDAY: set(),
    Days.TUESDAY: set(),
    Days.WEDNESDAY: set(),
    Days.THURSDAY: set(),
    Days.FRIDAY: set(),
    Days.SATURDAY: set(),
    Days.SUNDAY: set(),
    Days.TODAY: set(),
}
current_schedule: int = Days.TODAY


def try_int(inp: Any) -> int | None:
    try:
        return int(inp)
    except (ValueError, TypeError):
        return None


def get_timeline_indexes(hour_one: int, fifteens_one: int, duration_in_fifteens) -> tuple[int, int]:
    """
    :param hour_one:
    :param fifteens_one:
    :param duration_in_fifteens:
    :return:
    """
    start_index = hour_one * 4 + fifteens_one
    return start_index, start_index + duration_in_fifteens


def print_timeline_event_names() -> None:
    seen_events: set[Task] = set()
    print("Names of all events in current timeline:")
    for event in timeline:
        if event is None or event in seen_events:
            continue
        print(event.name)
        seen_events.add(event)


def add_to_timeline(task: Task) -> bool:
    start_index, end_index = get_timeline_indexes(task.hour_start, task.fifteens_into_hour, task.duration_in_fifteens)
    for index in range(start_index, end_index):
        if index >= timeline_length:
            print(f"Timeline index would have went out of bounds on task {task.name}")
            return False
        if timeline[index] is not None:
            print(f"Conflict with {timeline[index].name}")
            return False

    for index in range(start_index, end_index):
        timeline[index] = task
    return True


def get_event_start() -> tuple:
    """
    Either returns empty tuple or hour_start, fifteens_into_hour
    :return:
    """
    hour_start: int | None = try_int(input("Enter hour in military time: "))
    if hour_start is None or hour_start < 0 or hour_start > 23:
        print("Please enter an integer value between 0 and 23 inclusive")
        return tuple()

    fifteens_into_hour: int | None = try_int(input("Enter number (0 - 3) of 15 minutes into the hour: "))
    if fifteens_into_hour is None or fifteens_into_hour < 0 or fifteens_into_hour > 3:
        print("Please enter a integer value between 0 and 3 inclusive")
        return tuple()

    return hour_start, fifteens_into_hour


def get_event_duration() -> tuple:
    """
    Either returns empty tuple or hour_duration, fifteens_duration
    :return:
    """
    hour_duration: int | None = try_int(input("Enter how many hours, minutes will be asked after: "))
    if hour_duration is None or hour_duration < 0:
        print("Please enter an integer value >= 0")
        return tuple()

    fifteens_duration: int | None = try_int(input("How many 15 minute segments should be added on: "))
    if fifteens_duration is None or fifteens_duration < 0:
        print("Please enter an integer value >= 0")
        return tuple()

    if hour_duration == fifteens_duration == 0:
        print("Duration cannot be 0")
        return tuple()

    return hour_duration, fifteens_duration


def get_event_details() -> tuple:
    """
    Either returns empty tuple or hour_start, fifteens_into_hour, hour_duration, fifteens_duration
    :return:
    """
    event_start_input = get_event_start()
    if not event_start_input:
        return tuple()

    event_duration_input = get_event_duration()
    if not event_duration_input:
        return tuple()

    hour_start, fifteens_into_hour = event_start_input
    hour_duration, fifteens_duration = event_duration_input

    return hour_start, fifteens_into_hour, hour_duration, fifteens_duration


def add_event() -> None:
    input_result = get_event_details()

    if not input_result:
        return

    hour_start, fifteens_into_hour, hour_duration, fifteens_duration = input_result

    name: str = input("Name of this event: ")
    description: str = input("Description of event: ")

    new_task: Task = Task(
        name, description, hour_start, fifteens_into_hour, duration_in_fifteens=hour_duration * 4 + fifteens_duration
    )
    schedules[current_schedule].add(new_task)
    add_to_timeline(new_task)
    print(f"{new_task.name} was added")


def remove_event() -> None:
    print_timeline_event_names()
    event_name: str = input("Enter event name you want to remove: ")
    event_name_lower: str = event_name.lower()
    task_to_remove: Task | None = None
    curr: Task | None
    for index in range(timeline_length):
        curr = timeline[index]
        if curr is not None and curr.name.lower() == event_name_lower:
            task_to_remove = curr
            timeline[index] = None

    if task_to_remove:
        schedules[current_schedule].remove(task_to_remove)
        print(f"Event {event_name} removed")
    else:
        print(f"Event {event_name} not found")


def view_timeline() -> None:
    tasks_seen: set[Task] = set()
    curr: Task | None
    for index in range(timeline_length):
        curr = timeline[index]
        if curr is None or curr in tasks_seen:
            continue
        print(str(curr))
        tasks_seen.add(curr)

    if len(tasks_seen) == 0:
        print("Nothing on this schedule")


def clear_timeline() -> None:
    for index in range(timeline_length):
        timeline[index] = None


def remove_from_timeline(task_to_remove: Task) -> None:
    for index, task in enumerate(timeline):
        if task is not None and task.name == task_to_remove.name:
            timeline[index] = None


def clear_schedule() -> None:
    if input("Are you sure you want to clear your schedule? \"y\" or \"n\": ").lower() != "y":
        return

    schedules[current_schedule].clear()
    clear_timeline()


def create_timeline() -> None:
    for task in schedules[current_schedule]:
        add_to_timeline(task)


def get_weekday() -> int | None:
    return try_int(input(
        "Enter the number for the following schedules\n"
        "[0] Monday\n"
        "[1] Tuesday\n"
        "[2] Wednesday\n"
        "[3] Thursday\n"
        "[4] Friday\n"
        "[5] Saturday\n"
        "[6] Sunday\n"
        "[7] Today\n\n"
        "Number: "
    ))


def switch_schedule() -> None:
    global current_schedule
    inp = get_weekday()
    if inp is None or inp < 0 or inp > 7:
        print("Please enter an integer value between 0 - 7 inclusive")
        return
    current_schedule = inp
    clear_timeline()
    create_timeline()
    print(f"Current schedule set to {Days.get_str(current_schedule)}")


def help_display() -> None:
    print(
        "Description:\n"
        "This is a terminal based weekly scheduler with persistent storage.\n\n"
        "Schedules:\n"
        "This application saves 8 different schedules to your computer in a file called schedules.pkl stored in the\n"
        "same directory as the application. Seven of these are default daily schedules named the days of the week\n"
        "Monday - Sunday, these are the default schedules for each day of the week. The eighth schedule named Today\n"
        "represents the schedule you are following today.\n\n"
        "Commands/Display:\n"
        "Upon starting the application you will see a display that looks like\n\n"
        "Current Schedule: Today     - What schedule the following commands effect\n"  
        "[v] View current schedule   - Displays current schedule to screen\n"
        "[s] Switch schedules        - Switches to whatever schedule you select\n"
        "[c] Copy schedule           - Copy's schedule from one day to current schedule\n"
        "[k] Clear schedule          - Deletes all events from current schedule and clears the timeline\n"
        "[a] Add event               - Adds event to current schedule, if conflict it will be displayed\n"
        "[r] Remove event            - Removed event from current schedule\n"
        "[m] Modify event            - Modify, name, description, start time and/or duration of event\n"
        "[h] Help                    - Prints this useful help message :D\n"
        "[e] Exit                    - Exits application and saves all schedules\n\n"
        "ADDITIONAL NOTES:\n"
        "1) Exiting the program another way besides the [e] Exit will result in your schedules not being saved!\n"
        "2) Descriptions are optional when creating events (just hit enter)\n"
        "3) There might be some problems when you name two events the same thing so just don't do that\n"
        "4) I might be forgetting something here\n"
    )


def copy_schedule() -> None:
    print("Weekday schedule to copy")
    from_day: int | None = get_weekday()
    if not Days.valid_day(from_day):
        return

    if from_day == current_schedule:
        print(f"Copying from {Days.get_str(from_day)} to {Days.get_str(current_schedule)} will not result in any differences.")
        return

    os.system(cls_msg)
    schedules[current_schedule].clear()
    clear_timeline()
    schedules[current_schedule].update(deepcopy(schedules[from_day]))
    create_timeline()
    print(f"Put {Days.get_str(from_day)}'s schedule into {Days.get_str(current_schedule)}'s schedule")


def modify_event() -> None:
    print_timeline_event_names()
    event_name: str = input("Enter event name to modify: ")
    event_name_lower = event_name.lower()
    event: Task | None = None
    for e in schedules[current_schedule]:
        if e.name.lower() == event_name_lower:
            event = e
            break

    if event is None:
        print(f"Event {event_name} not found")
        return

    while True:
        os.system(cls_msg)
        inp = input(
            f"{event}\n"
            "[s] Change start time\n"
            "[d] Change duration\n"
            "[n] Change name\n"
            "[e] Change description\n"
            "[b] Go back\n"
            ": "
        ).lower()

        if inp == "s":
            start_input: tuple = get_event_start()
            if not start_input:
                continue
            hour_start, fifteens_into_hour = start_input
            old_hour = event.hour_start
            old_fifteens = event.fifteens_into_hour
            remove_from_timeline(event)
            event.hour_start = hour_start
            event.fifteens_into_hour = fifteens_into_hour
            if add_to_timeline(event):
                print(f"Successfully updated {event.name} start time")
            else:
                event.hour_start = old_hour
                event.fifteens_into_hour = old_fifteens
                add_to_timeline(event)
        elif inp == "d":
            duration_input = get_event_duration()
            if not duration_input:
                continue
            hour_duration, fifteens_duration = duration_input
            old_duration_in_fifteens = event.duration_in_fifteens
            remove_from_timeline(event)
            event.duration_in_fifteens = hour_duration * 4 + fifteens_duration
            if add_to_timeline(event):
                print(f"Successfully updated {event.name} duration")
            else:
                event.duration_in_fifteens = old_duration_in_fifteens
                add_to_timeline(event)
        elif inp == "b":
            return
        elif inp == "n":
            event.name = input("Enter new name: ")
        elif inp == "e":
            event.description = input("Enter new description: ")
        else:
            print("Invalid input")
        input("Enter to continue ...")


def exit_program() -> None:
    with open(FILE_NAME, "wb") as file:
        pickle.dump((schedules, date_opened), file)
    os.system(cls_msg)
    sys.exit(0)


def main() -> None:
    global timeline, schedules, current_schedule
    options: dict[str, Callable[[], None]] = {
        "v": view_timeline,
        "s": switch_schedule,
        "c": copy_schedule,
        "k": clear_schedule,
        "a": add_event,
        "r": remove_event,
        "m": modify_event,
        "h": help_display,
        "e": exit_program
    }
    display: str = (
        "[v] View current schedule\n"
        "[s] Switch schedules\n"
        "[c] Copy schedule\n"
        "[k] Clear schedule\n"
        "[a] Add event\n"
        "[r] Remove event\n"
        "[m] Modify event\n"
        "[h] Help\n"
        "[e] Exit\n"
    )

    try:
        with open(FILE_NAME, "rb") as file:
            schedules, date_last_opened = pickle.load(file)
            if date_last_opened != date_opened:
                if input(f"The day has changed since you last opened the scheduler.\n"
                         f"Would you like use the {Days.get_str(current_day.weekday())} schedule? \"y\" or \"n\": ").lower() == "y":
                    current_schedule = current_day.weekday()
                    schedules[Days.TODAY].clear()

    except FileNotFoundError:
        pass


    create_timeline()
    current_schedule = Days.TODAY
    os.system(cls_msg)
    while True:
        print(f"Current Schedule: {Days.get_str(current_schedule)}")
        print(display)
        inp: str = input("Enter option: ").lower()
        if inp not in options:
            print(f"{inp} is not an option")
        else:
            os.system(cls_msg)
            options[inp]()
        input("Enter to continue ...")
        os.system(cls_msg)


if __name__ == "__main__":
    main()
