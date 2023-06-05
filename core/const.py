"""Module of constants."""
from enum import StrEnum

EXCEL_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DATETIME_ISO_8610 = "%Y-%m-%dT%H:%M:%S%z"


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
    LARGER_THAN_TOWN_OR_LA = "Larger than Town or Local Authority"
    OTHER = "Other / Custom Geography"


class ImpactEnum(StrEnum):
    MARGINAL = "1 - Marginal Impact"
    LOW = "2 - Low Impact"
    MEDIUM = "3 - Medium Impact"
    SIGNIFICANT = "4 - Significant Impact"
    MAJOR = "5 - Major Impact"
    CRITICAL = "6 - Critical Impact"


class LikelihoodEnum(StrEnum):
    LOW = "1 - Low"
    MEDIUM = "2 - Medium"
    HIGH = "3 - High"


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


# some place names did not map correctly to an abbreviation, here is an inferrence of what they should be
SUPPLEMENTARY_ABBREVIATION_MAPPINGS = {
    "Stavely": "STV",
    "Sutton Town Centre High Street": "SUT",
}
FUND_ID_TO_NAME = {"FHSF": "High Street Fund", "TD": "Towns Fund"}
