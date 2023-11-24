# Create New Schedule Draft

You are a trip assistant. Here are some places I want to go, please help me generate a trip schedule in JSON file.

## Data Models

**Point** : a place I want to go

- name (str): The name of the place
- address (str): The full address of the place
- latLng (object): An object containing latitude and longitude coordinates

**RouteStep** : a single step in the route between two points

- start (str): The starting point's name of the step
- end (str): The ending point's name of the step
- step (str): The specific traffic route, e.g. 'Metro Line 11, 2 stops', 'Bus 91M, 3 stops', '500 metres on foot'
- duration (int): The time (in seconds) it takes to travel this step
- distance (int): The distance (in meters) between the start and end points

**Route** : a complete route from origin to destination

- origin (str): The starting point's name of the route
- destination (str): The ending point of the route
- steps (list\[RouteStep\]): An array of RouteStep objects representing each step in the route
- duration (int): The total time in seconds
- distance (int): The total distance in kilometers

**ScheduleBlock** : a block of time in the schedule for a specific activity

- type (str): The type of activity ('point' or 'route')
- point (str): The point where the activity takes place (if applicable)
- route (Route): The route taken to reach the point (if applicable)
- start (datetime): The start time of the activity in HH:mm format
- end (datetime): The end time of the activity in HH:mm format
- activity (str): A description of the activity

**ScheduleDay** : a single day in the trip schedule

- day (date): The date in the schedule (e.g. 2023/07/01)
- blocks (list\[ScheduleBlock\]): An array of ScheduleBlock objects representing the activities for the day

**Schedule** : the entire trip schedule

- start (date): The start date of the trip in YYYY/MM/DD format
- end (date): The end date of the trip
- days (list\[ScheduleDay\]): An array of ScheduleDay objects representing each day of the trip

## Input example

```json
{
  "start": "2023/07/01",
  "end": "2023/07/02",
  "points": [
    {
      "name": "Star Ferry",
      "address": "Star Ferry Pier, Tsim Sha Tsui, Tsim Sha Tsui Promenade, Hong Kong",
      "latLng": {
        "lat": 22.293764,
        "lng": 114.168463
      }
    },
    {
      "name": "Victoria Harbour",
      "address": "Tsim Sha Tsui Promenade, Kowloon, Hong Kong",
      "latLng": {
        "lat": 22.293528,
        "lng": 114.171007
      }
    },
    {
      "name": "Lantau Island",
      "address": "Lantau Island, New Territories, Hong Kong",
      "latLng": {
        "lat": 22.266498,
        "lng": 113.941751
      }
    }
  ]
}
```

## Output example

```json
{
    "start": "2023/07/01",
    "end": "2023/07/02",
    "days": [
        {
            "day": "2023/07/01",
            "blocks": [
                {
                    "type": "point",
                    "point": "Star Ferry",
                    "start": "10:00",
                    "end": "11:00",
                    "activity": "Take a ride on the Star Ferry and enjoy the view of Victoria Harbour"
                },
                {
                    "type": "route",
                    "route": {
                        "origin": "Star Ferry",
                        "destination": "Victoria Harbour",
                        "steps": [
                            {
                                "start": "Star Ferry",
                                "end": "Victoria Harbour",
                                "step": "350 metres on foot",
                                "distance": 350,
                                "duration": 300
                            }
                        ],
                        "duration": 300,
                        "distance": 350
                    },
                    "start": "11:00",
                    "end": "11:05",
                    "activity": "Walk to Victoria Harbour"
                },
                {
                    "type": "point",
                    "point": "Victoria Harbour",
                    "start": "11:05",
                    "end": "13:00",
                    "activity": "Explore Victoria Harbour and enjoy the skyline view"
                }
            ]
        },
        {
            "day": "2023/07/02",
            "blocks": [
                {
                    "type": "point",
                    "point": "Lantau Island",
                    "start": "10:00",
                    "end": "17:00",
                    "activity": "Spend the day exploring Lantau Island, visit the Big Buddha and Po Lin Monastery"
                }
            ]
        }
    ]
}

```
