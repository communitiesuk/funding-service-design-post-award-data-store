"""Module of constants."""
from enum import StrEnum

EXCEL_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DATETIME_ISO_8610 = "%Y-%m-%dT%H:%M:%S%z"
SUBMISSION_ID_FORMAT = "S-R{0:0=2d}-{1}"


class StatusEnum(StrEnum):
    NOT_YET_STARTED = "1. Not yet started"
    ONGOING_ON_TRACK = "2. Ongoing - on track"
    ONGOING_DELAYED = "3. Ongoing - delayed"
    COMPLETED = "4. Completed"
    OTHER = "5. Other"


class ProcurementStatusEnum(StrEnum):
    PUBLICATION_OF_ITT = "1. Publication of ITT"
    EVALUATION_OF_TENDERS = "2. Evaluation of Tenders"
    AWARDING_OF_CONSTRUCTION_CONTRACT = "3. Awarding of Construction Contract"
    SIGNING_OF_CONSTRUCTION_CONTRACT = "4. Signing of Construction Contract"


class StateEnum(StrEnum):
    ACTUAL = "Actual"
    FORECAST = "Forecast"


class PRAEnum(StrEnum):
    PRA = "PRA"
    OTHER = "Other"


class FundingSourceCategoryEnum(StrEnum):
    LOCAL_AUTHORITY = "Local Authority"
    THIRD_SECTOR_FUNDING = "Third Sector Funding"
    OTHER_PUBLIC_FUNDING = "Other Public Funding"
    PRIVATE_FUNDING = "Private Funding"


class GeographyIndicatorEnum(StrEnum):
    TRAVEL_CORRIDOR = "Travel corridor"
    LOCATIONS_PROVIDED_ELSEWHERE = "Locations provided in 'Project Admin' tab"
    OUTPUT_AREA = "Output area"
    LOWER_LAYER_SUPER_OUTPUT_AREA = "Lower layer super output area"
    MIDDLE_LAYER_SUPER_OUTPUT_AREA = "Middle layer super output area"
    TOWN = "Town"
    LOCAL_AUTHORITY = "Local Authority"
    LARGER_THAN_TOWN_OR_LA = "Larger than Town or Local Authority (e.g. Region)"
    OTHER = "Other / custom geography"


class ImpactEnum(StrEnum):
    MARGINAL = "1- Marginal impact"
    LOW = "2 - Low impact"
    MEDIUM = "3 - Medium impact"
    # trailing space on SIGNIFICANT and MAJOR is on purpose (the enum source in the submission Excel files match this)
    SIGNIFICANT = "4 - Significant impact "
    MAJOR = "5 - Major impact "
    CRITICAL = "6 - Critical impact"


class LikelihoodEnum(StrEnum):
    LOW = "1 - Low"
    MEDIUM = "2 - Medium"
    HIGH = "3 - High"
    ALMOST_CERTAIN = "4 - Almost Certain"


class ProximityEnum(StrEnum):
    REMOTE = "1 - Remote"
    DISTANT = "2 - Distant: next 12 months"
    APPROACHING = "3 - Approaching: next 6 months"
    CLOSE = "4 - Close: next 3 months"
    IMMINENT = "5 - Imminent: next month"


class MultiplicityEnum(StrEnum):
    SINGLE = "Single"
    MULTIPLE = "Multiple"


class RagEnum(StrEnum):
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"


class YesNoEnum(StrEnum):
    YES = "Yes"
    NO = "No"


class FundTypeIdEnum(StrEnum):
    TOWN_DEAL = "TD"
    HIGH_STREET_FUND = "HS"


# maps a fund id to its full name (we only store ids in the data model)
FUND_ID_TO_NAME = {FundTypeIdEnum.HIGH_STREET_FUND: "High Street Fund", FundTypeIdEnum.TOWN_DEAL: "Town Deal"}


# TLZ is given to any location outside the primary 12 ITL 1 regions as stated on the link below (previously NUTS & UKZ)
# This introduces the problem that TLZ now maps to multiple locations (Channel Islands, Isle of Man, Non-geographic)
# https://en.wikipedia.org/wiki/International_Territorial_Level
POSTCODE_AREA_TO_ITL1 = {
    "AB": "TLM",
    "AL": "TLH",
    "B": "TLG",
    "BA": "TLK",
    "BB": "TLD",
    "BD": "TLE",
    "BH": "TLK",
    "BL": "TLD",
    "BN": "TLJ",
    "BR": "TLI",
    "BS": "TLK",
    "BT": "TLN",
    "CA": "TLD",
    "CB": "TLH",
    "CF": "TLL",
    "CH": "TLD",
    "CM": "TLH",
    "CO": "TLH",
    "CR": "TLI",
    "CT": "TLJ",
    "CV": "TLG",
    "CW": "TLD",
    "DA": "TLI",
    "DD": "TLM",
    "DE": "TLF",
    "DG": "TLM",
    "DH": "TLC",
    "DL": "TLC",
    "DN": "TLE",
    "DT": "TLK",
    "DY": "TLG",
    "E": "TLI",
    "EC": "TLI",
    "EH": "TLM",
    "EN": "TLI",
    "EX": "TLK",
    "FK": "TLM",
    "FY": "TLD",
    "G": "TLM",
    "GL": "TLK",
    "GU": "TLJ",
    "GY": "TLZ",  # Channel Islands
    "HA": "TLI",
    "HD": "TLE",
    "HG": "TLE",
    "HP": "TLH",
    "HR": "TLG",
    "HS": "TLM",
    "HU": "TLE",
    "HX": "TLE",
    "IG": "TLI",
    "IM": "TLZ",  # Isle of Man
    "IP": "TLH",
    "IV": "TLM",
    "JE": "TLZ",  # Channel Islands
    "KA": "TLM",
    "KT": "TLI",
    "KW": "TLM",
    "KY": "TLM",
    "L": "TLD",
    "LA": "TLD",
    "LD": "TLL",
    "LE": "TLF",
    "LL": "TLL",
    "LN": "TLE",
    "LS": "TLE",
    "LU": "TLH",
    "M": "TLD",
    "ME": "TLJ",
    "MK": "TLJ",
    "ML": "TLM",
    "N": "TLI",
    "NE": "TLC",
    "NG": "TLF",
    "NN": "TLG",
    "NP": "TLL",
    "NR": "TLH",
    "NW": "TLI",
    "OL": "TLD",
    "OX": "TLJ",
    "PA": "TLM",
    "PE": "TLH",
    "PH": "TLM",
    "PL": "TLK",
    "PO": "TLJ",
    "PR": "TLD",
    "QC": "TLZ",  # Non-geographic
    "RG": "TLJ",
    "RH": "TLJ",
    "RM": "TLI",
    "S": "TLE",
    "SA": "TLL",
    "SE": "TLI",
    "SG": "TLH",
    "SK": "TLD",
    "SL": "TLJ",
    "SM": "TLI",
    "SN": "TLK",
    "SO": "TLJ",
    "SP": "TLK",
    "SR": "TLC",
    "SS": "TLH",
    "ST": "TLG",
    "SW": "TLI",
    "SY": "TLL",
    "TA": "TLK",
    "TD": "TLM",
    "TF": "TLG",
    "TN": "TLJ",
    "TQ": "TLK",
    "TR": "TLK",
    "TS": "TLE",
    "TW": "TLI",
    "UB": "TLI",
    "W": "TLI",
    "WA": "TLD",
    "WC": "TLI",
    "WD": "TLI",
    "WF": "TLE",
    "WN": "TLD",
    "WR": "TLG",
    "WS": "TLG",
    "WV": "TLG",
    "YO": "TLE",
    "ZE": "TLM",
}

# when constructing a project_id use this to look up the three letter abbreviation
# for example, a towns fund project in Barrow with a project number of 1 would become TD-BAR-01
PLACE_NAME_ABBREVIATIONS = {
    "Barnsley Town Centre": "BAR",
    "Barnstaple": "BST",
    "Barrow": "BAR",
    "Bedford": "BED",
    "Birkenhead": "BIR",
    "Bishop Auckland": "BIS",
    "Blackfriars - Northern City Centre": "WRC",
    "Blackpool": "BLA",
    "Bloxwich": "BLO",
    "Blyth": "BLY",
    "Blyth Town Centre": "BLY",
    "Bolton": "BOL",
    "Boston": "BOS",
    "Bournemouth": "BOU",
    "Bridgwater": "BRD",
    "Brierley Hill High Town Centre": "DUD",
    "Brighouse": "BRG",
    "Burton": "BUR",
    "Buxton": "BUX",
    "Camborne": "CAM",
    "Carlisle": "CAR",
    "Carlisle City Centre": "CAR",
    "Castleford": "CAS",
    "Chatham Town Centre": "CHA",
    "Cheadle": "CHE",
    "Clay Cross": "CLA",
    "Cleator Moor": "CLE",
    "Colchester": "COL",
    "Commercial Road": "POR",
    "Corby": "COR",
    "Crawley": "CRA",
    "Crewe": "CRE",
    "Darlington": "DRL",
    "Darwen": "DRW",
    "Derby City Centre, St Peters Cross": "DER",
    "Dewsbury": "DEW",
    "Doncaster": "DON",
    "Dover Town Centre and Waterfront": "DOV",
    "Dudley": "DUD",
    "Elland Town Centre": "ELL",
    "Farnworth": "FAR",
    "Fratton": "FRA",
    "Glastonbury": "GLA",
    "Goldthorpe": "GOL",
    "Goole": "GOO",
    "Grantham": "GRA",
    "Grays": "GRA",
    "Great Yarmouth": "GRE",
    "Grimsby": "GRI",
    "Grimsby Town Centre": "GRI",
    "Halifax": "HAL",
    "Harlow": "HRW",
    "Hartlepool": "HTL",
    "Hastings": "HAS",
    "Heanor": "HEA",
    "Hereford": "HER",
    "High Wycombe": "HIG",
    "Ipswich": "IPS",
    "Keighley": "KEI",
    "Kidderminster": "KID",
    "Kidsgrove": "KID",
    "King's Lynn": "KIN",
    "Kingswood": "KIN",
    "Kirkby and Sutton (Ashfield)": "KIR",
    "Kirkham Town Centre": "KIR",
    "Leamington Town Centre": "LEA",
    "Leyland": "LEY",
    "Lincoln": "LIN",
    "Loftus": "LOF",
    "Long Eaton": "LON",
    "Loughborough": "LOU",
    "Lowestoft": "LOW",
    "Mablethorpe": "MAB",
    "Mansfield": "MAN",
    "March High Street": "MRH",
    "Margate": "MAR",
    "Maryport Town Centre": "MYP",
    "Middlesbrough": "MID",
    "Middlesbrough Centre": "MID",
    "Millom": "MIL",
    "Milton Keynes": "MNK",
    "Morley": "MOR",
    "Nelson": "NEL",
    "New Ferry": "NWF",
    "Newark": "NWK",
    "Newcastle-Under-Lyme Town Centre": "NUL",
    "Newcastle-under-Lyme": "NUL",
    "Newhaven": "NWH",
    "Newton Abbot": "NWA",
    "Northallerton": "NRA",
    "Northampton": "NTH",
    "Norwich": "NOR",
    "Nottingham City Centre, West End Point": "NOT",
    "Nuneaton": "NUN",
    "Nuneaton Town Centre": "NUN",
    "Old Kent Road": "STH",
    "Oldham": "OLD",
    "Paignton": "PAI",
    "Penzance": "PEN",
    "Peterborough": "PET",
    "Plymouth City Centre": "PLY",
    "Preston": "PRE",
    "Putney Town Centre": "WAN",
    "Ramsgate": "RAM",
    "Redcar": "RDC",
    "Redditch": "RDT",
    "Rochdale": "RCH",
    "Rochdale Town Centre": "RCH",
    "Rotherham": "RTH",
    "Rowley Regis": "RWR",
    "Runcorn": "RCN",
    "Salisbury City Centre": "SAL",
    "Scarborough": "SCA",
    "Scunthorpe": "SCU",
    "Sheffield High Street": "SHE",
    "Shipley": "SHI",
    "Skegness": "SKE",
    "Smethwick": "SME",
    "South Shields": "SOS",
    "Southport": "SOU",
    "St Helens": "STH",
    "St Ives": "STI",
    "St Neots": "SNE",
    "Stafford": "STF",
    "Stainforth": "STF",
    "Stapleford": "STP",
    "Staveley": "STV",
    "Stevenage": "STE",
    "Stockport": "STO",
    "Stocksbridge": "STO",
    "Stockton": "STK",
    "Stretford": "STR",
    "Sunderland City Centre": "SUN",
    "Sutton": "SUT",
    "Sutton in Ashfield": "SIA",
    "Swindon": "SWI",
    "Tamworth Town Centre": "TAM",
    "Taunton": "TAU",
    "Telford": "TEL",
    "Thornaby": "THO",
    "Tilbury": "TIL",
    "Todmorden": "TOD",
    "Torquay": "TOR",
    "Tottenham High Road": "HRG",
    "Trowbridge": "TRO",
    "Truro": "TRU",
    "Wakefield": "WAK",
    "Walsall": "WAL",
    "Warrington": "WAR",
    "Wealdstone": "WEA",
    "West Bromwich": "WES",
    "Whitby": "WHI",
    "Wigan": "WIG",
    "Winsford": "WNS",
    "Wolverhampton": "WOL",
    "Wolverhampton City Centre (West)": "WOL",
    "Woolwich Town Centre": "GRN",
    "Worcester": "WRC",
    "Workington": "WRK",
    "Yeovil": "YEO",
}


TF_PLACE_NAMES_TO_ORGANISATIONS = {
    "Heanor": "Amber Valley Borough Council",
    "Kirkby and Sutton (Ashfield)": "Ashfield District Council",
    "Sutton in Ashfield": "Ashfield District Council",
    "Goldthorpe": "Barnsley Metropolitan Borough Council",
    "Barnsley Town Centre": "Barnsley Metropolitan Borough Council",
    "Bedford": "Bedford Borough Council",
    "Darwen": "Blackburn with Darwen Borough Council",
    "Blackpool": "Blackpool Borough Council",
    "Bolton": "Bolton Council",
    "Farnworth": "Bolton Council",
    "Boston": "Boston Borough Council",
    "Bournemouth": "Bournemouth, Christchurch and Poole Council",
    "Keighley": "Bradford Council",
    "Shipley": "Bradford Council",
    "Stapleford": "Broxtowe Borough Council",
    "High Wycombe": "Buckinghamshire Council",
    "Brighouse": "Calderdale Council",
    "Todmorden": "Calderdale Council",
    "Elland Town Centre": "Calderdale Council",
    "Halifax": "Calderdale Council",
    "Loughborough": "Charnwood Borough Council",
    "Crewe": "Cheshire East Council",
    "Winsford": "Cheshire West and Chester Council",
    "Staveley": "Chesterfield Borough Council",
    "Lincoln": "City of Lincoln Council",
    "Wolverhampton City Centre (West)": "City of Wolverhampton Council",
    "Wolverhampton": "City of Wolverhampton Council",
    "Colchester": "Colchester City Council",
    "Camborne": "Cornwall Council",
    "Penzance": "Cornwall Council",
    "St Ives": "Cornwall Council",
    "Truro": "Cornwall Council",
    "Crawley": "Crawley Borough Council",
    "Cleator Moor": "Cumberland Council",
    "Millom": "Cumberland Council",
    "Carlisle": "Cumberland Council",
    "Carlisle City Centre": "Cumberland Council",
    "Maryport Town Centre": "Cumberland Council",
    "Workington": "Cumberland Council",
    "Darlington": "Darlington Borough Council",
    "Derby City Centre, St Peters Cross": "Derby City Council",
    "Doncaster": "Doncaster Council",
    "Stainforth": "Doncaster Council",
    "Dover Town Centre and Waterfront": "Dover District Council",
    "Dudley": "Dudley Metropolitan Borough Council",
    "Brierley Hill High Town Centre": "Dudley Metropolitan Borough Council",
    "Bishop Auckland": "Durham County Council",
    "Mablethorpe": "East Lindsey District Council",
    "Skegness": "East Lindsey District Council",
    "Goole": "East Riding of Yorkshire Council",
    "Burton": "East Staffordshire Borough Council",
    "Lowestoft": "East Suffolk Council",
    "Long Eaton": "Erewash Borough Council",
    "March High Street": "Fenland District Council",
    "Kirkham Town Centre": "Fylde Council",
    "Great Yarmouth": "Great Yarmouth Borough Council",
    "Runcorn": "Halton Borough Council",
    "Tottenham High Road": "Haringey Council",
    "Harlow": "Harlow District Council",
    "Wealdstone": "Harrow Council",
    "Hartlepool": "Hartlepool Borough Council",
    "Hastings": "Hastings Borough Council",
    "Hereford": "Herefordshire Council",
    "Buxton": "High Peak Borough Council",
    "St Neots": "Huntingdonshire District Council",
    "Ipswich": "Ipswich",
    "Dewsbury": "Ipswich Borough Council",
    "King's Lynn": "King's Lynn and West Norfolk",
    "Morley": "Kirklees Council",
    "Newhaven": "Lewes District Council",
    "Sutton": "London Borough of Sutton Council",
    "Sutton High Street": "London Borough of Sutton Council",
    "Mansfield": "Mansfield District Council",
    "Chatham Town Centre": "Medway Council",
    "Middlesbrough": "Middlesbrough Council",
    "Middlesbrough Centre": "Middlesbrough Council",
    "Milton Keynes": "Milton Keynes City Council",
    "Newark-on-Trent": "Newark and Sherwood District Council",
    "Newark": "Newark and Sherwood District Council",
    "Kidsgrove": "Newcastle-under-Lyme Borough Council",
    "Newcastle-under-Lyme": "Newcastle-under-Lyme Borough Council",
    "Newcastle-under-Lyme Town Centre": "Newcastle-under-Lyme Borough Council",
    "Newcastle-Under-Lyme Town Centre": "Newcastle-under-Lyme Borough Council",
    "Barnstaple": "North Devon Council",
    "Clay Cross": "North East Derbyshire District Council",
    "Grimsby": "North East Lincolnshire Council",
    "Grimsby Town Centre": "North East Lincolnshire Council",
    "Scunthorpe": "North Lincolnshire Council",
    "Corby": "North Northamptonshire Council",
    "Scarborough": "North Yorkshire Council",
    "Whitby": "North Yorkshire Council",
    "Northallerton": "North Yorkshire Council",
    "Blyth": "Northumberland County Council",
    "Blyth Town Centre": "Northumberland County Council",
    "Norwich": "Norwich City Council",
    "Nottingham City Centre, West End Point": "Nottingham City Council",
    "Nuneaton Town Centre": "Nuneaton & Bedworth Borough Council",
    "Nuneaton": "Nuneaton and Bedworth",
    "Oldham": "Oldham Metropolitan Borough Council",
    "Nelson": "Pendle Borough Council",
    "Peterborough": "Peterborough City Council",
    "Plymouth City Centre": "Plymouth City Council",
    "Commercial Road": "Portsmouth City Council",
    "Fratton": "Portsmouth City Council",
    "Preston": "Preston City Council",
    "Loftus": "Redcar & Cleveland Borough Council",
    "Redcar": "Redcar & Cleveland Borough Council",
    "Redditch": "Redditch Borough Council ",
    "Rochdale": "Rochdale Borough Council",
    "Rochdale Town Centre": "Rochdale Borough Council",
    "Rotherham": "Rotherham Metropolitan Borough Council",
    "Woolwich Town Centre": "Royal Borough of Greenwich",
    "Rowley Regis": "Sandwell Council",
    "Smethwick": "Sandwell Council",
    "West Bromwich": "Sandwell Council",
    "Southport": "Sefton Metropolitan Borough Council",
    "Stocksbridge": "Sheffield City Council",
    "Sheffield High Street": "Sheffield City Council",
    "Bridgwater": "Somerset Council",
    "Glastonbury": "Somerset Council",
    "Taunton": "Somerset Council",
    "Yeovil": "Somerset Council",
    "Kingswood": "South Gloucestershire Council",
    "Grantham": "South Kesteven District Council",
    "Leyland": "South Ribble Borough Council",
    "South Shields": "South Tyneside Council",
    "Old Kent Road": "Southwark Council",
    "St Helens": "St Helens Borough Council",
    "Stafford": "Stafford Borough Council",
    "Stevenage": "Stevenage Borough Council",
    "Cheadle": "Stockport Metropolitan Borough Council",
    "Stockport": "Stockport Metropolitan Borough Council",
    "Thornaby": "Stockton-On-Tees Borough Council",
    "Stockton": "Stockton-On-Tees Borough Council",
    "Sunderland City Centre": "Sunderland City Council",
    "Swindon": "Swindon Borough Council",
    "Tamworth Town Centre": "Tamworth Borough Council",
    "Newton Abbot": "Teignbridge District Council",
    "Telford": "Telford & Wrekin Council ",
    "Margate": "Thanet District Council",
    "Ramsgate": "Thanet District Council",
    "Grays": "Thurrock Borough Council",
    "Tilbury": "Thurrock Borough Council",
    "Torquay": "Torbay Council",
    "Paignton": "Torbay Council",
    "Stretford": "Trafford Council",
    "Castleford": "Wakefield Metropolitan Borough Council",
    "Wakefield": "Wakefield Metropolitan Borough Council",
    "Bloxwich": "Walsall Council",
    "Walsall": "Walsall Council",
    "Putney Town Centre": "Wandsworth Council",
    "Warrington": "Warrington Borough Council",
    "Leamington Town Centre": "Warwick District Council",
    "Northampton": "West Northamptonshire Council",
    "Barrow": "Westmorland & Furness Council ",
    "Wigan": "Wigan Council",
    "Salisbury City Centre": "Wiltshire Council",
    "Trowbridge": "Wiltshire Council",
    "Birkenhead": "Wirral Council",
    "New Ferry": "Wirral Council",
    "Worcester": "Worcester City Council",
    "Blackfriars - Northern City Centre": "Worcester City Council",
    "Kidderminster": "Wyre Forest District Council",
}

# some place names did not map correctly to an abbreviation, here is an inference of what they should be
SUPPLEMENTARY_ABBREVIATION_MAPPINGS = {
    "Stavely": "STV",
    "Sutton Town Centre High Street": "SUT",
}

# Hard-coded map of Outputs to categories, as provided by TF 09/06/2023
OUTPUT_CATEGORIES = {
    "# of additional enterprises with broadband access of at least 30mbps": "Regeneration - Community Infrastructure",
    (
        "# of additional residential units " "with broadband access of at least 30mbps"
    ): "Regeneration - Community Infrastructure",
    "# of alternative fuel charging/re-fuelling points": "Transport",
    "# of derelict buildings refurbished": "Regeneration - Estate Renewal",
    "# of enterprises receiving financial support other than grants": "Business",
    "# of enterprises receiving grants": "Business",
    "# of enterprises receiving non-financial support": "Business",
    "# of heritage buildings renovated/restored": "Culture",
    "# of improved public transport routes": "Transport",
    "# of learners enrolled in new education and training courses": "Education",
    (
        "# of learners/students/trainees gaining certificates, graduating or"
        " completing courses at new or improved training or education facilities, or attending new courses"
    ): "Education",
    "# of learners/trainees/students enrolled at improved education and training facilities": "Education",
    "# of learners/trainees/students enrolled at new education and training facilities": "Education",
    "# of new or improved car parking spaces": "Transport",
    "# of new public transport routes": "Transport",
    "# of potential entrepreneurs assisted to be enterprise ready": "Business",
    "# of residential units improved/refurbished": "Regeneration - Housing",
    "# of residential units provided": "Regeneration - Housing",
    "# of sites cleared": "Regeneration - Estate Renewal",
    "# of transport nodes with new multimodal connection points": "Transport",
    "# of trees planted": "Regeneration - Public Realm",
    "% of 5G coverage in town": "Regeneration - Community Infrastructure",
    "% of Wi-fi coverage in town": "Regeneration - Community Infrastructure",
    "Amount of capacity of new or improved training or education facilities": "Regeneration - Community Infrastructure",
    "Amount of existing parks/greenspace/outdoor improved": "Regeneration - Public Realm",
    "Amount of floor space repurposed (residential, commercial, retail)": "Regeneration - Urban Regeneration",
    "Amount of floorspace rationalised": "Regeneration - Urban Regeneration",
    "Amount of manufacturing space renovated/improved": "Regeneration - Commercial Property",
    "Amount of new manufacturing space": "Regeneration - Commercial Property",
    "Amount of new office space": "Regeneration - Commercial Property",
    (
        "Amount of new 'other' enterprise space (not captured by the other categories)"
    ): "Regeneration - Commercial Property",
    "Amount of new parks/greenspace/outdoor space": "Regeneration - Public Realm",
    "Amount of new public realm": "Regeneration - Public Realm",
    "Amount of new retail, leisure or food & beverage space": "Regeneration - Commercial Property",
    "Amount of office space renovated/improved": "Regeneration - Commercial Property",
    (
        "Amount of 'other' enterprise space (not captured by the other categories) renovated/improved"
    ): "Regeneration - Commercial Property",
    "Amount of public realm improved": "Regeneration - Public Realm",
    "Amount of rehabilitated land": "Regeneration - Estate Renewal",
    "Amount of retail, leisure or food & beverage space space renovated/improved": "Regeneration - Commercial Property",
    "Number of closer collaborations with employers": "Business",
    "Number of improved cultural facilities": "Regeneration - Community Infrastructure",
    "Number of new community/sports centres": "Regeneration - Community Infrastructure",
    "Number of new cultural facilities": "Regeneration - Community Infrastructure",
    "Number of non-domestic buildings with green retrofits completed": "Regeneration - Estate Renewal",
    "Number of public amenities/facilities created": "Regeneration - Public Amenities",
    "Number of public amenities/facilities relocated": "Regeneration - Public Amenities",
    "Number of residential units with green retrofits completed": "Regeneration - Estate Renewal",
    "Total length of improved cycle ways": "Transport",
    "Total length of new cycle ways": "Transport",
    "Total length of new pedestrian paths": "Transport",
    "Total length of newly built roads": "Transport",
    "Total length of pedestrian paths improved": "Transport",
    "Total length of resurfaced/improved road": "Transport",
    "Total length of roads converted to cycling or pedestrian ways": "Transport",
    "# of temporary FT jobs supported": "Mandatory",
    "# of full-time equivalent (FTE) permanent jobs created through the project": "Mandatory",
    "# of full-time equivalent (FTE) permanent jobs safeguarded through the project": "Mandatory",
}

# Hard-coded map of Outcomes to categories, as provided by TF 09/06/2023
OUTCOME_CATEGORIES = {
    "Air quality - NO2 concentrations": "Transport",
    "Air quality - PM2.5 concentrations": "Transport",
    "Audience numbers for cultural events": "Culture",
    "Automatic / manual counts of pedestrians and cyclists (for active travel schemes)": "Transport",
    "Average (mean) anxiety ratings": "Health & Wellbeing",
    "Average (mean) happiness ratings": "Health & Wellbeing",
    "Average (mean) life satisfaction ratings": "Health & Wellbeing",
    "Average (mean) worthwhile ratings": "Health & Wellbeing",
    "Average occupancy rate of units or workspaces": "Economy",
    "Average travel time in minutes to reach nearest large employment centre (5000+ employees): Car": "Transport",
    "Average travel time in minutes to reach nearest large employment centre (5000+ employees): Cycle": "Transport",
    (
        "Average travel time in minutes to reach nearest large employment centre (5000+ employees): Public Transport"
    ): "Transport",
    "Average travel time in minutes to reach nearest large employment centre (5000+ employees): Walking": "Transport",
    "Business investment": "Economy",
    "Business sentiment": "Economy",
    "Change in air quality": "Health & Wellbeing",
    "Consumer spending": "Economy",
    "Count of active enterprises": "Economy",
    "Count of births of new enterprises": "Economy",
    "Cycle flow": "Transport",
    "Estimated carbon dioxide equivalent reductions as a result of support": "Health & Wellbeing",
    "Number of anti-social behaviour crimes recorded": "Place",
    "Number of crimes reported": "Place",
    "Number of cultural events": "Culture",
    "Number of day visitors": "Place",
    "Number of enterprises receiving non-financial support": "Business",
    "Number of major commercial planning applications granted": "Economy",
    "Number of minor commercial planning applications granted": "Economy",
    "Number of non-residential/domestic units upgraded to EPC rating C or above": "Regeneration",
    "Number of people using a new/improved public facility": "Place",
    "Number of residential/domestic units upgraded to EPC rating C or above": "Health & Wellbeing",
    "Number of road traffic accidents": "Transport",
    "Number of students completing Further Education courses": "Education",
    "Number of students completing Higher Education courses": "Education",
    "Number of students enrolling in Further Education courses": "Education",
    "Number of students enrolling in Higher Education courses": "Education",
    "Number of visitors/audience members to cultural venues": "Culture",
    "Passenger numbers": "Transport",
    "Patronage of the public transport system in the area of interest (for public transport schemes)": "Transport",
    "Pedestrian flow": "Place",
    'Percentage of adults who are considered "active"': "Health & Wellbeing",
    "Percentage of adults who are satisfied with their local area as a place to live": "Place",
    'Percentage of children and young people who are considered "active"': "Health & Wellbeing",
    "Percentage of customers/visitors/users who report a positive experience": "Place",
    "Percentage of individuals who have engaged in civic participation in the last 12 months": "Place",
    "Percentage of residents who report a sense of belonging in their local area": "Place",
    "Percentage of residents who report feeling safe in their local area": "Place",
    "Percentage of the local poulation engaged with cultural and heritage activities": "Culture",
    "Percentage of visitors who are likely to recommend the place to family or friends": "Place",
    "Percentage of visitors who report feeling safe in the local area": "Place",
    "Public transport reliability": "Transport",
    "Public transport trips as a proportion of total trips per year": "Transport",
    "Road traffic flows in corridors of interest (for road schemes)": "Transport",
    "Total visitor spend at cultural venues": "Culture",
    "Towns Self-Assessment Questions": "Place",
    "Travel times in the corridors of interest": "Transport",
    "User satisfaction (transport)": "Transport",
    "Usual method of travel to work: Bicycle": "Transport",
    "Usual method of travel to work: Bus, Minibus or Coach": "Transport",
    "Usual method of travel to work: Car or Van": "Transport",
    "Usual method of travel to work: E-Cycle, E-Scooter": "Transport",
    "Usual method of travel to work: Motorbike, Moped, Scooter": "Transport",
    "Usual method of travel to work: Other Way of Travelling": "Transport",
    "Usual method of travel to work: Railway Train": "Transport",
    "Usual method of travel to work: Taxi": "Transport",
    "Usual method of travel to work: Underground Train, Metro, Light Railway, Tram": "Transport",
    "Usual method of travel to work: Walk": "Transport",
    "Vacancy rate of commercial units": "Economy",
    "Vacancy rate of residential units": "Place",
    "Vehicle delays": "Transport",
    "Vehicle flow": "Transport",
    "Vehicle journey time": "Transport",
    "Year on Year monthly % change in footfall": "Place",
    "Year-on-year % change in monthly footfall": "Place",
}

# A dictionary mapping ingest form periods to ingestion rounds
REPORTING_PERIOD_DICT = {
    "2019/20 to 31 March 2022": 1,
    "1 April 2022 to 30 September 2022": 2,
    "1 October 2022 to 31 March 2023": 3,
    "1 April 2023 to 30 September 2023": 4,
    "1 October 2023 to 31 March 2024": 5,
    "1 April 2024 to 30 September 2024": 6,
    "1 October 2024 to 31 March 2025": 7,
    "1 April 2025 to 30 September 2025": 8,
    "1 October 2025 to 31 March 2026": 9,
}

# Sheets we expect to be in the Round 3 ingestion form
EXPECTED_ROUND_THREE_SHEETS = [
    "1 - Start Here",
    "2 - Project Admin",
    "3 - Programme Progress",
    "4a - Funding Profiles",
    "4b - PSI",
    "5 - Project Outputs",
    "6 - Outcomes",
    "7 - Risk Register",
    "8 - Review & Sign-Off",
]

# Sheets not present in a given round
EXCLUDED_TABLES_BY_ROUND = {
    1: ["Private Investments", "Outputs_Ref", "Output_Data"],
    2: ["Private Investments", "Funding Comments"],
}

# Column sort orders for each dataframe prior to export to Excel
TABLE_SORT_ORDERS = {
    "PlaceDetails": ["SubmissionID", "Question", "Indicator"],
    "ProjectDetails": ["SubmissionID", "ProjectID"],
    "OrganisationRef": ["OrganisationName"],
    "ProgrammeRef": ["ProgrammeName", "FundTypeID"],
    "ProgrammeProgress": ["SubmissionID", "Question"],
    "ProjectProgress": ["SubmissionID", "ProjectID"],
    "FundingQuestions": ["SubmissionID", "ProgrammeID", "Question", "Indicator"],
    "Funding": [
        "SubmissionID",
        "ProjectID",
        "FundingSourceName",
        "FundingSourceType",
        "Secured",
        "StartDate",
        "EndDate",
    ],
    "FundingComments": ["SubmissionID", "ProjectID"],
    "PrivateInvestments": ["SubmissionID", "ProjectID"],
    "OutputsRef": ["OutputName"],
    "OutputData": [
        "SubmissionID",
        "ProjectID",
        "Output",
        "FinancialPeriodStart",
        "FinancialPeriodEnd",
        "UnitofMeasurement",
    ],
    "OutcomeRef": ["OutcomeName"],
    "OutcomeData": ["SubmissionID", "ProjectID", "Outcome", "StartDate", "EndDate", "GeographyIndicator"],
    "RiskRegister": ["SubmissionID", "ProgrammeID", "ProjectID", "RiskName"],
}
