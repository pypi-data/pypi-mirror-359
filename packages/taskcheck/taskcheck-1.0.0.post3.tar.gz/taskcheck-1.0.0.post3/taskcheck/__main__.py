import tomllib
import argparse

from taskcheck.parallel import check_tasks_parallel
from taskcheck.common import config_dir

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "-v", "--verbose", action="store_true", help="Increase output verbosity."
)
arg_parser.add_argument(
    "-i",
    "--install",
    action="store_true",
    help="Install the UDAs, required settings, and default config file.",
)
arg_parser.add_argument(
    "-r",
    "--report",
    action="store",
    help="Generate a report of the tasks based on the scheduling; can be any Taskwarrior datetime specification (e.g. today, tomorrow, eom, som, 1st, 2nd, etc.). It is considered as `by`, meaning that the report will be generated for all the days until the specified date and including it.",
)
arg_parser.add_argument(
    "-s",
    "--schedule",
    action="store_true",
    help="Perform the scheduling algorithm, giving a schedule and a scheduling UDA and alerting for not completable tasks.",
)
arg_parser.add_argument(
    "-f",
    "--force-update",
    action="store_true",
    help="Force update of all ical calendars by ignoring cache expiration.",
)
arg_parser.add_argument(
    "--taskrc",
    action="store",
    help="Set custom TASKRC directory for debugging purposes.",
)
arg_parser.add_argument(
    "--urgency-weight",
    type=float,
    help="Weight for urgency in scheduling (0.0 to 1.0), overrides config value. When 1.0, the whole Taskwarrior urgency is used for scheduling. When 0.0, the Taskwarrior urgency is reduced to only due urgency.",
)
arg_parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Perform scheduling without modifying the Taskwarrior database, useful for testing.",
)
arg_parser.add_argument(
    "--no-auto-adjust-urgency",
    dest="auto_adjust_urgency",
    action="store_false",
    default=True,
    help="Disable automatic reduction of urgency weight when tasks cannot be completed on time. (Enabled by default, meaning automatic reduction will occur.)",
)


# Load working hours and exceptions from TOML file
def load_config():
    """
    Loads the configuration from the TOML file located at config_dir / "taskcheck.toml".
    Returns a dictionary with the config structure, e.g.:
    {
        "time_maps": {
            "work": {
                "monday": [[9, 12.30], [14, 17]],
                "tuesday": [[9, 12.30], [14, 17]],
                ...
            }
        },
        "scheduler": {
            "days_ahead": 365,
            "weight_urgency": 1.0,
            ...
        },
        "report": {
            "include_unplanned": true,
            "additional_attributes": [],
            "additional_attributes_unplanned": [],
            "emoji_keywords": {},
            ...
        }
    }
    """
    with open(config_dir / "taskcheck.toml", "rb") as f:
        config = tomllib.load(f)
    return config


def main():
    args = arg_parser.parse_args()

    # Load data and check tasks
    print_help = True
    result = None
    if args.install:
        from taskcheck.install import install

        install()
        return

    if args.schedule:
        config = load_config()
        check_tasks_kwargs = dict(
            verbose=args.verbose,
            force_update=args.force_update,
            taskrc=args.taskrc,
            urgency_weight_override=args.urgency_weight,
            dry_run=args.dry_run,
            auto_adjust_urgency=args.auto_adjust_urgency,
        )
        # Only add auto_adjust_urgency if it is present and a real bool (not a mock)
        result = check_tasks_parallel(
            config,
            **check_tasks_kwargs,
        )
        print_help = False

    if args.report:
        from taskcheck.report import generate_report

        config = load_config()
        scheduling_results = None
        if args.schedule and args.dry_run:
            # If we just did a dry-run schedule, use those results
            scheduling_results = result
        generate_report(
            config,
            args.report,
            args.verbose,
            force_update=args.force_update,
            taskrc=args.taskrc,
            scheduling_results=scheduling_results,
        )
        print_help = False

    if print_help:
        arg_parser.print_help()


if __name__ == "__main__":
    main()
