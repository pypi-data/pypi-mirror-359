# Entities
The following entities are extracted

## Wellness
The `wellness` entity contains the following data:

```python
fields = [
    "id",
    "ctl",
    "atl",
    "rampRate",
    "ctlLoad",
    "atlLoad",
    "sportInfo",
    "updated",
    "weight",
    "restingHR",
    "hrv",
    "hrvSDNN",
    "menstrualPhase",
    "menstrualPhasePredicted",
    "kcalConsumed",
    "sleepSecs",
    "sleepScore",
    "sleepQuality",
    "avgSleepingHR",
    "soreness",
    "fatigue",
    "stress",
    "mood",
    "motivation",
    "injury",
    "spO2",
    "systolic",
    "diastolic",
    "hydration",
    "hydrationVolume",
    "readiness",
    "baevskySI",
    "bloodGlucose",
    "lactate",
    "bodyFat",
    "abdomen",
    "vo2max",
    "comments",
]
```
### Special fields
There are some special fields that contains a complex data, like `sportInfo`. This field is not extracted yet, because needs an extra process to save it into InfluxDB.

### InfluxDB data
The information is stored with the following format:

- measurement: "wellness"
- tags:
    - "day": "id"
- fields: every field defined above
- time: "id" (in timestamp)

## Activity
The `Acvivity` entity contains the following information:

```python
fields = [
    "id",
    "start_date_local",
    "type",
    "icu_ignore_time",
    "icu_pm_cp",
    "icu_pm_w_prime",
    "icu_pm_p_max",
    "icu_pm_ftp",
    "icu_pm_ftp_secs",
    "icu_pm_ftp_watts",
    "icu_ignore_power",
    "icu_rolling_cp",
    "icu_rolling_w_prime",
    "icu_rolling_p_max",
    "icu_rolling_ftp",
    "icu_rolling_ftp_delta",
    "icu_training_load",
    "icu_atl",
    "icu_ctl",
    "paired_event_id",
    "name",
    "description",
    "start_date",
    "distance",
    "icu_distance",
    "moving_time",
    "elapsed_time",
    "coasting_time",
    "total_elevation_gain",
    "timezone",
    "trainer",
    "commute",
    "max_speed",
    "average_speed",
    "device_watts",
    "has_heartrate",
    "max_heartrate",
    "average_heartrate",
    "average_cadence",
    "calories",
    "average_temp",
    "min_temp",
    "max_temp",
    "avg_lr_balance",
    "gap",
    "gap_model",
    "use_elevation_correction",
    "race",
    "gear",
    "perceived_exertion",
    "device_name",
    "power_meter",
    "power_meter_serial",
    "power_meter_battery",
    "crank_length",
    "external_id",
    "file_sport_index",
    "file_type",
    "icu_athlete_id",
    "created",
    "icu_sync_date",
    "analyzed",
    "icu_ftp",
    "icu_w_prime",
    "threshold_pace",
    "icu_hr_zones",
    "pace_zones",
    "lthr",
    "icu_resting_hr",
    "icu_weight",
    "icu_power_zones",
    "icu_sweet_spot_min",
    "icu_sweet_spot_max",
    "icu_power_spike_threshold",
    "trimp",
    "icu_warmup_time",
    "icu_cooldown_time",
    "icu_chat_id",
    "icu_ignore_hr",
    "ignore_velocity",
    "ignore_pace",
    "icu_weighted_avg_watts",
    "icu_training_load_data",
    "interval_summary",
    "stream_types",
    "has_segments",
    "power_field_names",
    "power_field",
    "icu_zone_times",
    "icu_hr_zone_times",
    "pace_zone_times",
    "gap_zone_times",
    "use_gap_zone_times",
    "tiz_order",
    "icu_achievements",
    "icu_intervals_edited",
    "lock_intervals",
    "icu_lap_count",
    "icu_joules",
    "icu_joules_above_ftp",
    "icu_max_wbal_depletion",
    "icu_recording_time",
    "icu_hrr",
    "icu_sync_error",
    "icu_color",
    "icu_power_hr_z2",
    "icu_power_hr_z2_mins",
    "icu_cadence_z2",
    "icu_rpe",
    "feel",
    "kg_lifted",
    "decoupling",
    "icu_median_time_delta",
    "p30s_exponent",
    "workout_shift_secs",
    "strava_id",
    "lengths",
    "pool_length",
    "compliance",
    "source",
    "oauth_client_id",
    "oauth_client_name",
    "power_load",
    "hr_load",
    "pace_load",
    "hr_load_type",
    "pace_load_type",
    "tags",
    "recording_stops",
    "pace",
    "athlete_max_hr",
    "group",
    "icu_average_watts",
    "icu_intensity",
    "icu_variability_index",
    "icu_efficiency_factor",
    "icu_power_hr",
    "session_rpe",
    "average_stride",
]
```

### Special fields
Like Wellness, some special fields can not be exported yet. The next "special fields" are extracted, with their created field in InfluxDB:

```python
"icu_hr_zones" => "icu_hr_zones_0","icu_hr_zones_1",...
"pace_zones" => "pace_zones_0","pace_zones_1"
"icu_power_zones" => "icu_power_zones_0","icu_power_zones_1",...
"icu_zone_times" => "icu_zone_times_z1","icu_zone_times_z2",...
"icu_hr_zone_times" => "icu_hr_zone_times_0","icu_hr_zone_times_1",...
"pace_zone_times" => "pace_zone_times_0","pace_zone_times_1",...
"gap_zone_times" => "gap_zone_times_0","gap_zone_times_1",...
```

The next "special fields" are NOT extracted yet:

```python
"gear",
"interval_summary",
"power_field_names",
"icu_hrr",
"stream_types",
"recording_stops",
"icu_achievements",
```

### InfluxDB data
The information is stored with the following format:

- measurement: "activity"
- tags:
    - "type": "type"
    - "id": "id"
    - "start_date": "start_date_local" (in format YYYY-MM-DD)
- fields: every field defined above
- time: "id" (in timestamp)

## Streams
The following types of `Streams` are retrieved:

```python
"time",
"watts",
"cadence",
"heartrate",
"distance",
"altitude",
"latlng",
"velocity_smooth",
"temp",
"torque",
"respiration",
```

### InfluxDB data
The information is stored with the following format:

- measurement: "stream"
- tags:
    - "activity_type": activity["type"]
    - "activity_id": activity["id"]
    - "stream_type": "stream["type"]
- fields:
    - "data": the value of every stream
- time: activity["time"] (in timestamp) + stream_element_number (every stream value corresponds to a second, so every stream adds 1 second to the start time. If we have 340 streams, we have 340 entries with +1 second between)