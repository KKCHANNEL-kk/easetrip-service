# Mock Points

You are a trip attractions database. Here are some places I want to go with their names, please help me mock some attractions data in JSON file.

## Data Model

**Point**:

- id: int
- name: str
- latLng: LatLng
- address: str
- mapid: Optional[str]
- pic: Optional[List[str]] = []
- tag: List[str] = [] // limit in TagList
- city: str
- introduction: str
- options: Dict[Any, Any] = {}

**TagList**: valid tag options

['Seasonal Limited','Delicious Food','Historical Sites','Citywalk','Cultural Expriences',Playgrounds','Events & Shows']
