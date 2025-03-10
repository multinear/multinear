def select_tasks(config, challenge_id=None, group_id=None):
    """
    Select tasks to run based on config and filters.

    Args:
        config: The experiment configuration
        challenge_id: Optional challenge ID to filter tasks
        group_id: Optional group ID to filter tasks

    Returns:
        List of task groups
    """
    all_tasks = []

    if "groups" in config:
        # Using groups structure
        if group_id:
            # Filter to only include tasks from the specified group
            for group in config["groups"]:
                if group.get("id") == group_id and "tasks" in group:
                    if challenge_id:
                        # Filter tasks by challenge_id
                        clean_challenge_id = challenge_id
                        if (
                            "_" in challenge_id
                            and challenge_id.split("_")[1].isdigit()
                        ):
                            clean_challenge_id = challenge_id.split("_")[0]
                        tasks = [
                            t
                            for t in group["tasks"]
                            if t.get("id") == clean_challenge_id
                        ]
                        if tasks:
                            all_tasks.append({"group_id": group_id, "tasks": tasks})
                    else:
                        all_tasks.append(
                            {"group_id": group_id, "tasks": group["tasks"]}
                        )
                    break
            if not all_tasks:
                raise ValueError(
                    f"No group found with ID {group_id} or no matching tasks"
                )
        else:
            # Include tasks from all groups
            for group in config["groups"]:
                if "tasks" in group:
                    group_tasks = group["tasks"]
                    if challenge_id:
                        # Filter tasks by challenge_id
                        clean_challenge_id = challenge_id
                        if (
                            "_" in challenge_id
                            and challenge_id.split("_")[1].isdigit()
                        ):
                            clean_challenge_id = challenge_id.split("_")[0]
                        group_tasks = [
                            t
                            for t in group_tasks
                            if t.get("id") == clean_challenge_id
                        ]
                    if group_tasks:
                        all_tasks.append(
                            {
                                "group_id": group.get("id", "unknown"),
                                "tasks": group_tasks,
                            }
                        )
    elif "tasks" in config:
        # Using traditional tasks structure
        tasks = config["tasks"]
        if challenge_id:
            # Filter tasks by challenge_id
            clean_challenge_id = challenge_id
            if "_" in challenge_id and challenge_id.split("_")[1].isdigit():
                clean_challenge_id = challenge_id.split("_")[0]
            tasks = [t for t in tasks if t.get("id") == clean_challenge_id]
        if tasks:
            all_tasks.append({"group_id": None, "tasks": tasks})

    if not all_tasks:
        raise ValueError("No tasks to run found in config.yaml")

    return all_tasks
