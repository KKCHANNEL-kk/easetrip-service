prompts = {
    'start_new_schedule_draft':
        {
            'system': '''
You are a trip assistant. Here are some places I want to go, please help me generate a trip schedule in JSON file. No need to chat.

## Data Models

**Point** : a place I want to go

- id (int): The ID of the place
- name (str): The name of the place
- address (str): The full address of the place
- latLng (object): An object containing latitudeitude and longitude coordinates

**RouteStep** : a single step in the route between two points

- start (str): The starting point's name of the step
- end (str): The ending point's name of the step
- step (str): The specific traffic route, e.g. 'Metro Line 11, 2 stops', 'Bus 91M, 3 stops', '500 metres on foot'
- duration (int): The time (in seconds) it takes to travel this step
- distance (int): The distance (in meters) between the start and end points

**Route** : a complete route from origin to destination

- origin (Point): The starting point's name of the route
- destination (Point): The ending point of the route
- steps (list[RouteStep]): An array of RouteStep objects representing each step in the route
- duration (int): The total time in seconds
- distance (int): The total distance in kilometers

**ScheduleBlock** : a block of time in the schedule for a specific activity

- type (str): The type of activity ('point' or 'route')
- point (Point): The point where the activity takes place (if applicable)
- route (Route): The route taken to reach the point (if applicable)
- start (datetime): The start time of the activity in HH:mm format
- end (datetime): The end time of the activity in HH:mm format
- activity (str): A description of the activity

**ScheduleDay** : a single day in the trip schedule

- day (date): The date in the schedule (e.g. 2023-07-01)
- blocks (list[ScheduleBlock]): An array of ScheduleBlock objects representing the activities for the day

**Schedule** : the entire trip schedule

- start (date): The start date of the trip in yyyy-mm-dd format
- end (date): The end date of the trip
- days (list[ScheduleDay]): An array of ScheduleDay objects representing each day of the trip

''',
            'examples': [
                {'role': 'user',
                 'content':
                 '''
{
  "start": "2023-07-01",
  "end": "2023-07-02",
  "points": [
    {
      "id": 1,
      "name": "Star Ferry",
      "address": "Star Ferry Pier, Tsim Sha Tsui, Tsim Sha Tsui Promenade, Hong Kong",
      "latLng": {
        "latitude": 22.293764,
        "longitude": 114.168463
      }
    },
    {
      "id": 2,
      "name": "Victoria Harbour",
      "address": "Tsim Sha Tsui Promenade, Kowloon, Hong Kong",
      "latLng": {
        "latitude": 22.293528,
        "longitude": 114.171007
      }
    },
    {
      "id": 3,
      "name": "Lantau Island",
      "address": "Lantau Island, New Territories, Hong Kong",
      "latLng": {
        "latitude": 22.266498,
        "longitude": 113.941751
      }
    }
  ]
}
'''}, {
                    'role': 'assistant',
                    'content':
                    '''
{
  "start": "2023-07-01",
  "end": "2023-07-02",
  "days": [
    {
      "day": "2023-07-01",
      "blocks": [
        {
          "type": "point",
          "point": {
            "id": 1,
            "name": "Star Ferry",
            "address": "Star Ferry Pier, Tsim Sha Tsui, Tsim Sha Tsui Promenade, Hong Kong",
            "latLng": {
              "latitude": 22.293764,
              "longitude": 114.168463
            }
          },
          "start": "10:00",
          "end": "11:00",
          "activity": "Take a ride on the Star Ferry and enjoy the view of Victoria Harbour"
        },
        {
          "type": "route",
          "route": {
            "origin": {
              "id": 1,
              "name": "Star Ferry",
              "address": "Star Ferry Pier, Tsim Sha Tsui, Tsim Sha Tsui Promenade, Hong Kong",
              "latLng": {
                "latitude": 22.293764,
                "longitude": 114.168463
              }
            },
            "destination": {
              "id": 2,
              "name": "Victoria Harbour",
              "address": "Tsim Sha Tsui Promenade, Kowloon, Hong Kong",
              "latLng": {
                "latitude": 22.293528,
                "longitude": 114.171007
              }
            },
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
          "point": {
            "id": 2,
            "name": "Victoria Harbour",
            "address": "Tsim Sha Tsui Promenade, Kowloon, Hong Kong",
            "latLng": {
              "latitude": 22.293528,
              "longitude": 114.171007
            }
          },
          "start": "11:05",
          "end": "13:00",
          "activity": "Explore Victoria Harbour and enjoy the skyline view"
        }
      ]
    },
    {
      "day": "2023-07-02",
      "blocks": [
        {
          "type": "point",
          "point": {
            "id": 3,
            "name": "Lantau Island",
            "address": "Lantau Island, New Territories, Hong Kong",
            "latLng": {
              "latitude": 22.266498,
              "longitude": 113.941751
            }
          },
          "start": "10:00",
          "end": "17:00",
          "activity": "Spend the day exploring Lantau Island, visit the Big Buddha and Po Lin Monastery"
        }
      ]
    }
  ]
}
'''
                }
            ]
        },
    'refine_schedule': {
        'examples': [
            {'role': 'user',
             'content': 'help me add some resturants in my schedule'},
            {'role': 'assistant',
             'content': '''
{
    "start": "2023-07-01",
    "end": "2023-07-03",
    "days": [
        {
            "day": "2023-07-01",
            "blocks": [
                {
                    "type": "point",
                    "point": {
                        "id": 8,
                        "name": "The Forbidden City",
                        "latLng": {
                            "latitude": 39.916344,
                            "longitude": 116.397155
                        },
                        "address": "4 Jingshan Front St, Dongcheng, Beijing, China",
                    },
                    "route": null,
                    "start": "10:00:00",
                    "end": "13:00:00",
                    "activity": "Explore the Forbidden City and learn about Chinese history"
                },
                {
                    "type": "route",
                    "point": null,
                    "route": {
                        "origin": {
                        "id": 8,
                        "name": "The Forbidden City",
                        "latLng": {
                            "latitude": 39.916344,
                            "longitude": 116.397155
                        },
                        "address": "4 Jingshan Front St, Dongcheng, Beijing, China",
                    },
                        "destination": "The Great Wall of China",
                        "steps": [
                            {
                                "start": "The Forbidden City",
                                "end": "Dongzhimen Station",
                                "step": "Metro Line 5, 4 stops",
                                "duration": 600,
                                "distance": 4000
                            },
                            {
                                "start": "Dongzhimen Station",
                                "end": "Huairou North Avenue Station",
                                "step": "Metro Line 13, 10 stops",
                                "duration": 1800,
                                "distance": 20000
                            },
                            {
                                "start": "Huairou North Avenue Station",
                                "end": "The Great Wall of China",
                                "step": "Bus H23, 5 stops",
                                "duration": 600,
                                "distance": 5000
                            }
                        ],
                        "duration": 3000,
                        "distance": 29000
                    },
                    "start": "14:00:00",
                    "end": "16:00:00",
                    "activity": "Travel to the Great Wall of China"
                },
                {
                    "type": "point",
                    "point": {
                        "id": 9,
                        "name": "The Great Wall of China",
                        "latLng": {
                            "latitude": 40.431908,
                            "longitude": 116.570374
                        },
                        "address": "Huairou, Beijing, China"
                    },
                    "route": null,
                    "start": "16:00:00",
                    "end": "18:00:00",
                    "activity": "Explore the Great Wall of China and enjoy the scenic view"
                },
                {
                    "type": "point",
                    "point": "Da Dong Roast Duck Restaurant",
                    "route": null,
                    "start": "19:00:00",
                    "end": "21:00:00",
                    "activity": "Enjoy a delicious dinner at Da Dong Roast Duck Restaurant"
                }
            ]
        },
        {
            "day": "2023-07-02",
            "blocks": [
                {
                    "type": "point",
                    "point": {
                        "id": 9,
                        "name": "The Great Wall of China",
                        "latLng": {
                            "latitude": 40.431908,
                            "longitude": 116.570374
                        },
                        "address": "Huairou, Beijing, China"
                    },
                    "route": null,
                    "start": "10:00:00",
                    "end": "13:00:00",
                    "activity": "Continue exploring the Great Wall of China"
                },
                {
                    "type": "route",
                    "point": null,
                    "route": {
                        "origin": "The Great Wall of China",
                        "destination": "The Forbidden City",
                        "steps": [
                            {
                                "start": "The Great Wall of China",
                                "end": "Huairou North Avenue Station",
                                "step": "Bus H23, 5 stops",
                                "duration": 600,
                                "distance": 5000
                            },
                            {
                                "start": "Huairou North Avenue Station",
                                "end": "Dongzhimen Station",
                                "step": "Metro Line 13, 10 stops",
                                "duration": 1800,
                                "distance": 20000
                            },
                            {
                                "start": "Dongzhimen Station",
                                "end": "The Forbidden City",
                                "step": "Metro Line 5, 4 stops",
                                "duration": 600,
                                "distance": 4000
                            }
                        ],
                        "duration": 3000,
                        "distance": 29000
                    },
                    "start": "14:00:00",
                    "end": "16:00:00",
                    "activity": "Travel back to the Forbidden City"
                },
                {
                    "type": "point",
                    "point": "Quanjude Roast Duck Restaurant",
                    "route": null,
                    "start": "19:00:00",
                    "end": "21:00:00",
                    "activity": "Enjoy a delicious dinner at Quanjude Roast Duck Restaurant"
                },
                {
                    "type": "point",
                    "point": {
                        "id": 8,
                        "name": "The Forbidden City",
                        "latLng": {
                            "latitude": 39.916344,
                            "longitude": 116.397155
                        },
                        "address": "4 Jingshan Front St, Dongcheng, Beijing, China"
                    },
                    "route": null,
                    "start": "21:00:00",
                    "end": "22:00:00",
                    "activity": "Explore the Forbidden City and enjoy the sunset view"
                }
            ]
        }
    ]
}
             '''
             }
        ]
    }
}
