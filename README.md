# Voice Agent Scenarios

The voice agent loads its configuration from `config.json`.

Use `switch_config.py` to select which scenario should be active.

## Available Scenarios

* `appointment_scheduling`
* `reschedule_cancel`
* `medication_refill`
* `office_information`
* `edge_cases`

## Switch Scenarios

```bash
python switch_config.py appointment_scheduling
```

```bash
python switch_config.py reschedule_cancel
```

```bash
python switch_config.py medication_refill
```

```bash
python switch_config.py office_information
```

```bash
python switch_config.py edge_cases
```

This copies the selected configuration from the `configs/` folder into `config.json`.

## Start the Agent

After selecting a scenario:

```bash
python main.py
```

Example:

```bash
python switch_config.py medication_refill
python main.py
```

## Adding a New Scenario

1. Create a new JSON file in `configs/`.
2. Add the scenario configuration.
3. Activate it with:

```bash
python switch_config.py <scenario_name>
```

No changes to `main.py` are required.
