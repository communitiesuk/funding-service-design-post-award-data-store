from enum import StrEnum

PRE_VALIDATION_ERROR_LOG = "Pre-validation error: {error}"
PRE_VALIDATION_LOG = "Pre-validation error(s) found during upload"
VALIDATION_ERROR_LOG = "Validation error: {error}"
VALIDATION_LOG = "Validation error(s) found during upload"


class MIMETYPE(StrEnum):
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    JSON = "application/json"


FUND_TYPE_ID_TO_FRIENDLY_NAME = {
    "TD": "Town Deal",
    "HS": "Future High Streets Fund",
}

# domain/email: (LAs, Places, Funds)
TOWNS_FUND_AUTH = {
    "ambervalley.gov.uk": (("Amber Valley Borough Council",), ("Heanor",), ("Town_Deal", "Future_High_Street_Fund")),
    "ashfield.gov.uk": (
        ("Ashfield District Council",),
        ("Sutton in Ashfield", "Kirkby and Sutton (Ashfield)"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "barnsley.gov.uk": (
        ("Barnsley Metropolitan Borough Council",),
        ("Barnsley Town Centre", "Goldthorpe"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "bedford.gov.uk": (("Bedford Borough Council",), ("Bedford",), ("Town_Deal", "Future_High_Street_Fund")),
    "blackburn.gov.uk": (
        ("Blackburn with Darwen Borough Council",),
        ("Darwen",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "blackpool.gov.uk": (("Blackpool Borough Council",), ("Blackpool",), ("Town_Deal", "Future_High_Street_Fund")),
    "bolton.gov.uk": (
        ("Bolton Metropolitan Borough Council",),
        ("Farnworth", "Bolton"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "boston.gov.uk": (("Boston Borough Council",), ("Boston",), ("Town_Deal", "Future_High_Street_Fund")),
    "bradford.gov.uk": (("Bradford Council",), ("Shipley", "Keighley"), ("Town_Deal", "Future_High_Street_Fund")),
    "broxtowe.gov.uk": (("Broxtowe Borough Council",), ("Stapleford",), ("Town_Deal", "Future_High_Street_Fund")),
    "buckinghamshire.gov.uk": (
        ("Buckinghamshire Council",),
        ("High Wycombe",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "buckscc.gov.uk": (("Buckinghamshire Council",), ("High Wycombe",), ("Town_Deal", "Future_High_Street_Fund")),
    "calderdale.gov.uk": (
        ("Calderdale Council",),
        ("Halifax", "Brighouse", "Todmorden", "Elland Town Centre"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "cannockchasedc.gov.uk": (
        ("Ashfield District Council",),
        ("Sutton in Ashfield", "Kirkby and Sutton (Ashfield)"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "charnwood.gov.uk": (("Charnwood Borough Council",), ("Loughborough",), ("Town_Deal", "Future_High_Street_Fund")),
    "cheshireeast.gov.uk": (("Cheshire East Council",), ("Crewe",), ("Town_Deal", "Future_High_Street_Fund")),
    "cheshirewestandchester.gov.uk": (
        ("Cheshire West and Chester Council",),
        ("Winsford",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "chesterfield.gov.uk": (("Chesterfield Borough Council",), ("Staveley",), ("Town_Deal", "Future_High_Street_Fund")),
    "colchester.gov.uk": (("Colchester City Council",), ("Colchester",), ("Town_Deal", "Future_High_Street_Fund")),
    "cornwall.gov.uk": (
        ("Cornwall Council",),
        ("Truro", "Camborne", "Penzance", "St Ives"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "durham.gov.uk": (("Durham County Council",), ("Bishop Auckland",), ("Town_Deal", "Future_High_Street_Fund")),
    "herefordshire.gov.uk": (("Herefordshire Council",), ("Hereford",), ("Town_Deal", "Future_High_Street_Fund")),
    "crawley.gov.uk": (("Crawley Borough Council",), ("Crawley",), ("Town_Deal", "Future_High_Street_Fund")),
    # Cumberland and Carlisle have merged and need identical access, however both domains are still in use
    "cumberland.gov.uk": (
        ("Cumberland Council",),
        ("Workington", "Cleator Moor", "Millom", "Carlisle", "Carlisle City Centre", "Maryport Town Centre"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "carlisle.gov.uk": (
        ("Cumberland Council",),
        ("Workington", "Cleator Moor", "Millom", "Carlisle", "Carlisle City Centre", "Maryport Town Centre"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "darlington.gov.uk": (("Darlington Borough Council",), ("Darlington",), ("Town_Deal", "Future_High_Street_Fund")),
    "derby.gov.uk": (
        ("Derby City",),
        ("Derby City Centre, St Peters Cross",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "doncaster.gov.uk": (
        ("Doncaster Metropolitan Borough Council",),
        (
            "Stainforth",
            "Doncaster",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "dover.gov.uk": (
        ("Dover District Council",),
        ("Dover Town Centre and Waterfront",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "dudley.gov.uk": (
        ("Dudley Metropolitan Borough Council",),
        (
            "Brierley Hill High Town Centre",
            "Dudley",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "e-lindsey.gov.uk": (
        ("East Lindsey District Council",),
        (
            "Skegness",
            "Mablethorpe",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "eastriding.gov.uk": (
        ("East Riding of Yorkshire Council",),
        ("Goole",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "eaststaffsbc.gov.uk": (
        ("East Staffordshire Borough Council",),
        ("Burton",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "erewash.gov.uk": (("Erewash Borough Council",), ("Long Eaton",), ("Town_Deal", "Future_High_Street_Fund")),
    "fenland.gov.uk": (("Fenland District Council",), ("March High Street",), ("Town_Deal", "Future_High_Street_Fund")),
    "fylde.gov.uk": (("Fylde Council",), ("Kirkham Town Centre",), ("Town_Deal", "Future_High_Street_Fund")),
    "great-yarmouth.gov.uk": (
        ("Great Yarmouth Borough Council",),
        ("Great Yarmouth",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "royalgreenwich.gov.uk": (
        ("Royal Borough of Greenwich",),
        ("Woolwich Town Centre",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "halton.gov.uk": (("Halton Borough Council",), ("Runcorn",), ("Town_Deal", "Future_High_Street_Fund")),
    "haringey.gov.uk": (
        ("London Borough of Haringey",),
        ("Tottenham High Road",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "harlow.gov.uk": (("Harlow District Council",), ("Harlow",), ("Town_Deal", "Future_High_Street_Fund")),
    "harrow.gov.uk": (("London Borough of Harrow",), ("Wealdstone",), ("Town_Deal", "Future_High_Street_Fund")),
    "hartlepool.gov.uk": (("Hartlepool Borough Council",), ("Hartlepool",), ("Town_Deal", "Future_High_Street_Fund")),
    "hastings.gov.uk": (("Hastings Borough Council",), ("Hastings",), ("Town_Deal", "Future_High_Street_Fund")),
    "highpeak.gov.uk": (("High Peak Borough Council",), ("Buxton",), ("Town_Deal", "Future_High_Street_Fund")),
    "huntingdonshire.gov.uk": (
        ("Huntingdonshire District Council",),
        ("St Neots",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "ipswich.gov.uk": (("Ipswich Borough Council",), ("Ipswich",), ("Town_Deal", "Future_High_Street_Fund")),
    "west-norfolk.gov.uk": (
        ("King's Lynn and West Norfolk",),
        ("King's Lynn",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "kirklees.gov.uk": (("Kirklees Council",), ("Dewsbury",), ("Town_Deal", "Future_High_Street_Fund")),
    "leeds.gov.uk": (("Leeds Council",), ("Morley",), ("Town_Deal", "Future_High_Street_Fund")),
    "lewes-eastbourne.gov.uk": (
        ("Lewes District Council",),
        ("Eastbourne Borough Council", "Newhaven"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "ad.lewes-eastbourne.gov.uk": (
        ("Lewes District Council",),
        ("Eastbourne Borough Council", "Newhaven"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "lincoln.gov.uk": (("City of Lincoln Council",), ("Lincoln",), ("Town_Deal", "Future_High_Street_Fund")),
    "mansfield.gov.uk": (("Mansfield District Council",), ("Mansfield",), ("Town_Deal", "Future_High_Street_Fund")),
    "medway.gov.uk": (("Medway Council",), ("Chatham Town Centre",), ("Town_Deal", "Future_High_Street_Fund")),
    "mendip.gov.uk": (
        ("Somerset Council",),
        (
            "Yeovil",
            "Bridgwater",
            "Glastonbury",
            "Taunton",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "middlesbrough.gov.uk": (
        ("Middlesbrough Council",),
        (
            "Middlesbrough Centre",
            "Middlesbrough",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "milton-keynes.gov.uk": (
        ("Milton Keynes City Council",),
        ("Milton Keynes",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "newark-sherwooddc.gov.uk": (
        ("Newark and Sherwood District Council",),
        (
            "Newark",
            "Newark-on-Trent",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "newcastle-staffs.gov.uk": (
        ("Newcastle-under-Lyme Borough Council",),
        (
            "Newcastle-Under-Lyme Town Centre",
            "Kidsgrove",
            "Newcastle-under-Lyme",
            "Newcastle-under-Lyme Town Centre",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "northdevon.gov.uk": (("North Devon Council",), ("Barnstaple",), ("Town_Deal", "Future_High_Street_Fund")),
    "ne-derbyshire.gov.uk": (
        ("North East Derbyshire District Council",),
        ("Clay Cross",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "nelincs.gov.uk": (
        ("North East Lincolnshire Council",),
        (
            "Grimsby Town Centre",
            "Grimsby",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "northlincs.gov.uk": (("North Lincolnshire Council",), ("Scunthorpe",), ("Town_Deal", "Future_High_Street_Fund")),
    "northumberland.gov.uk": (
        ("Northumberland County Council",),
        (
            "Blyth Town Centre",
            "Blyth",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "northyorks.gov.uk": (
        ("North Yorkshire Council",),
        (
            "Northallerton",
            "Scarborough",
            "Whitby",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "hambleton.gov.uk": (
        ("North Yorkshire Council",),
        (
            "Northallerton",
            "Scarborough",
            "Whitby",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "scarborough.gov.uk": (
        ("North Yorkshire Council",),
        (
            "Northallerton",
            "Scarborough",
            "Whitby",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "norwich.gov.uk": (("Norwich City Council",), ("Norwich",), ("Town_Deal", "Future_High_Street_Fund")),
    "nottinghamcity.gov.uk": (
        ("Nottingham City Council",),
        ("Nottingham City Centre - West End Point",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "nuneatonandbedworth.gov.uk": (
        ("Nuneaton & Bedworth Borough Council",),
        (
            "Nuneaton Town Centre",
            "Nuneaton",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "oldham.gov.uk": (("Oldham Metropolitan Borough Council",), ("Oldham",), ("Town_Deal", "Future_High_Street_Fund")),
    "pendle.gov.uk": (("Pendle Borough Council",), ("Nelson",), ("Town_Deal", "Future_High_Street_Fund")),
    "peterborough.gov.uk": (
        ("Peterborough City Council",),
        ("Peterborough",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "plymouth.gov.uk": (
        ("Plymouth City Council",),
        ("Plymouth City Centre",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "portsmouth.gov.uk": (
        ("Portsmouth City Council",),
        (
            "Fratton",
            "Commercial Road",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "portsmouthcc.gov.uk": (
        ("Portsmouth City Council",),
        ("Fratton", "Commercial Road"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "preston.gov.uk": (("Preston City Council",), ("Preston",), ("Town_Deal", "Future_High_Street_Fund")),
    "redcar-cleveland.gov.uk": (
        ("Redcar & Cleveland Borough Council",),
        (
            "Redcar",
            "Loftus",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "redditchbc.gov.uk": (("Redditch Borough Council",), ("Redditch",), ("Town_Deal", "Future_High_Street_Fund")),
    "rochdale.gov.uk": (
        ("Rochdale Borough Council",),
        ("Rochdale Town Centre", "Rochdale"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "rotherham.gov.uk": (
        ("Rotherham Metropolitan Borough Council",),
        ("Rotherham",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "sandwell.gov.uk": (
        ("Sandwell Council",),
        ("West Bromwich", "Rowley Regis", "Smethwick"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "sefton.gov.uk": (
        ("Sefton Metropolitan Borough Council",),
        ("Southport",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "sheffield.gov.uk": (
        ("Sheffield City Council",),
        ("Sheffield High Street", "Stocksbridge"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "somerset.gov.uk": (
        ("Somerset Council",),
        ("Yeovil", "Bridgwater", "Glastonbury", "Taunton"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "southglos.gov.uk": (("South Gloucestershire Council",), ("Kingswood",), ("Town_Deal", "Future_High_Street_Fund")),
    "southkesteven.gov.uk": (
        ("South Kesteven District Council",),
        ("Grantham",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "southribble.gov.uk": (("South Ribble Borough Council",), ("Leyland",), ("Town_Deal", "Future_High_Street_Fund")),
    "chorley.gov.uk": (("South Ribble Borough Council",), ("Leyland",), ("Town_Deal", "Future_High_Street_Fund")),
    "southtyneside.gov.uk": (("South Tyneside Council",), ("South Shields",), ("Town_Deal", "Future_High_Street_Fund")),
    "southwark.gov.uk": (
        ("London Borough of Southwark",),
        ("Old Kent Road",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "staffordbc.gov.uk": (("Stafford Borough Council",), ("Stafford",), ("Town_Deal", "Future_High_Street_Fund")),
    "stevenage.gov.uk": (("Stevenage Borough Council",), ("Stevenage",), ("Town_Deal", "Future_High_Street_Fund")),
    "sthelens.gov.uk": (("St Helens Council",), ("St Helens",), ("Town_Deal", "Future_High_Street_Fund")),
    "stockport.gov.uk": (
        ("Stockport Metropolitan Borough Council",),
        ("Stockport", "Cheadle"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "stockton.gov.uk": (
        ("Stockton-on-Tees Borough Council",),
        ("Stockton", "Thornaby"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "sunderland.gov.uk": (
        ("Sunderland City Council",),
        ("Sunderland City Centre",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "sutton.gov.uk": (
        ("London Borough of Sutton",),
        ("London Borough of Sutton Council", "Sutton"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "swindon.gov.uk": (("Swindon Borough Council",), ("Swindon",), ("Town_Deal", "Future_High_Street_Fund")),
    "tamworth.gov.uk": (
        ("Tamworth Borough Council",),
        ("Tamworth Town Centre",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "teignbridge.gov.uk": (
        ("Teignbridge District Council",),
        ("Newton Abbot",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "telford.gov.uk": (("Telford & Wrekin Council",), ("Telford",), ("Town_Deal", "Future_High_Street_Fund")),
    "thanet.gov.uk": (("Thanet District Council",), ("Ramsgate", "Margate"), ("Town_Deal", "Future_High_Street_Fund")),
    "thurrock.gov.uk": (("Thurrock Borough Council",), ("Tilbury", "Grays"), ("Town_Deal", "Future_High_Street_Fund")),
    "torbay.gov.uk": (("Torbay Council",), ("Paignton", "Torquay"), ("Town_Deal", "Future_High_Street_Fund")),
    "trafford.gov.uk": (("Trafford Council",), ("Stretford",), ("Town_Deal", "Future_High_Street_Fund")),
    "wakefield.gov.uk": (
        ("Wakefield Metropolitan District Council",),
        ("Wakefield", "Castleford"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "walsall.gov.uk": (("Walsall Council",), ("Walsall", "Bloxwich"), ("Town_Deal", "Future_High_Street_Fund")),
    "richmondandwandsworth.gov.uk": (
        ("London Borough of Wandsworth",),
        ("Putney Town Centre",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "warrington.gov.uk": (("Warrington Borough Council",), ("Warrington",), ("Town_Deal", "Future_High_Street_Fund")),
    "warwickdc.gov.uk": (
        ("Warwick District Council",),
        ("Leamington Town Centre",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "westmorlandandfurness.gov.uk": (
        ("Westmorland & Furness Council",),
        ("Barrow",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "wigan.gov.uk": (("Wigan Council",), ("Wigan",), ("Town_Deal", "Future_High_Street_Fund")),
    "wiltshire.gov.uk": (
        ("Wiltshire Council",),
        ("Trowbridge", "Salisbury City Centre"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "wirral.gov.uk": (("Wirral Council",), ("New Ferry", "Birkenhead"), ("Town_Deal", "Future_High_Street_Fund")),
    "wolverhampton.gov.uk": (
        ("City of Wolverhampton Council",),
        ("Wolverhampton", "Wolverhampton City Centre (West)"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "worcester.gov.uk": (
        ("Worcester City Council",),
        ("Blackfriars - Northern City Centre", "Worcester"),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "wyreforestdc.gov.uk": (
        ("Wyre Forest District Council",),
        ("Kidderminster",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "bcpcouncil.gov.uk": (
        ("Bournemouth, Christchurch and Poole Council",),
        ("Bournemouth",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "eastsuffolk.gov.uk": (("East Suffolk Council",), ("Lowestoft",), ("Town_Deal", "Future_High_Street_Fund")),
    "northnorthants.gov.uk": (
        ("North Northamptonshire Council",),
        ("Corby",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
    "corby.gov.uk": (("North Northamptonshire Council",), ("Corby",), ("Town_Deal", "Future_High_Street_Fund")),
    "westnorthants.gov.uk": (
        ("West Northamptonshire Council",),
        ("Northampton",),
        ("Town_Deal", "Future_High_Street_Fund"),
    ),
}
