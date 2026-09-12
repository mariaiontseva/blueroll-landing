# The 33 London local authorities for the borough rating pages.
# LocalAuthorityId is the FSA API id; council is the name used in FAQ copy;
# neighbours power the "Nearby" link mesh (slugs, 3-5 each, mutual where sane).
BOROUGHS = {
    "barking-and-dagenham": {"id": 88, "name": "Barking and Dagenham", "council": "Barking and Dagenham Council", "neighbours": ["newham", "redbridge", "havering"]},
    "barnet": {"id": 89, "name": "Barnet", "council": "Barnet Council", "neighbours": ["enfield", "haringey", "camden", "brent", "harrow"]},
    "bexley": {"id": 90, "name": "Bexley", "council": "Bexley Council", "neighbours": ["greenwich", "bromley"]},
    "brent": {"id": 91, "name": "Brent", "council": "Brent Council", "neighbours": ["harrow", "barnet", "camden", "ealing", "westminster"]},
    "bromley": {"id": 92, "name": "Bromley", "council": "Bromley Council", "neighbours": ["bexley", "greenwich", "lewisham", "croydon"]},
    "camden": {"id": 93, "name": "Camden", "council": "Camden Council", "neighbours": ["barnet", "haringey", "islington", "westminster", "brent"]},
    "city-of-london": {"id": 95, "name": "the City of London", "council": "the City of London Corporation", "neighbours": ["westminster", "islington", "hackney", "tower-hamlets", "southwark"]},
    "croydon": {"id": 94, "name": "Croydon", "council": "Croydon Council", "neighbours": ["bromley", "sutton", "merton", "lambeth"]},
    "ealing": {"id": 96, "name": "Ealing", "council": "Ealing Council", "neighbours": ["hillingdon", "harrow", "brent", "hounslow", "hammersmith-and-fulham"]},
    "enfield": {"id": 97, "name": "Enfield", "council": "Enfield Council", "neighbours": ["barnet", "haringey", "waltham-forest"]},
    "greenwich": {"id": 98, "name": "Greenwich", "council": "the Royal Borough of Greenwich", "neighbours": ["bexley", "lewisham", "bromley", "tower-hamlets"]},
    "hackney": {"id": 99, "name": "Hackney", "council": "Hackney Council", "neighbours": ["islington", "haringey", "waltham-forest", "tower-hamlets", "city-of-london"]},
    "hammersmith-and-fulham": {"id": 100, "name": "Hammersmith and Fulham", "council": "Hammersmith and Fulham Council", "neighbours": ["kensington-and-chelsea", "ealing", "wandsworth", "hounslow"]},
    "haringey": {"id": 101, "name": "Haringey", "council": "Haringey Council", "neighbours": ["enfield", "barnet", "camden", "islington", "hackney"]},
    "harrow": {"id": 102, "name": "Harrow", "council": "Harrow Council", "neighbours": ["hillingdon", "ealing", "brent", "barnet"]},
    "havering": {"id": 103, "name": "Havering", "council": "Havering Council", "neighbours": ["barking-and-dagenham", "redbridge"]},
    "hillingdon": {"id": 104, "name": "Hillingdon", "council": "Hillingdon Council", "neighbours": ["harrow", "ealing", "hounslow"]},
    "hounslow": {"id": 105, "name": "Hounslow", "council": "Hounslow Council", "neighbours": ["hillingdon", "ealing", "richmond-upon-thames", "hammersmith-and-fulham"]},
    "islington": {"id": 106, "name": "Islington", "council": "Islington Council", "neighbours": ["camden", "haringey", "hackney", "city-of-london"]},
    "kensington-and-chelsea": {"id": 107, "name": "Kensington and Chelsea", "council": "the Royal Borough of Kensington and Chelsea", "neighbours": ["westminster", "hammersmith-and-fulham", "brent"]},
    "kingston-upon-thames": {"id": 108, "name": "Kingston upon Thames", "council": "Kingston Council", "neighbours": ["richmond-upon-thames", "merton", "sutton", "wandsworth"]},
    "lambeth": {"id": 109, "name": "Lambeth", "council": "Lambeth Council", "neighbours": ["southwark", "wandsworth", "merton", "croydon", "westminster"]},
    "lewisham": {"id": 110, "name": "Lewisham", "council": "Lewisham Council", "neighbours": ["greenwich", "southwark", "bromley", "tower-hamlets"]},
    "merton": {"id": 111, "name": "Merton", "council": "Merton Council", "neighbours": ["wandsworth", "lambeth", "croydon", "sutton", "kingston-upon-thames"]},
    "newham": {"id": 112, "name": "Newham", "council": "Newham Council", "neighbours": ["tower-hamlets", "waltham-forest", "redbridge", "barking-and-dagenham"]},
    "redbridge": {"id": 113, "name": "Redbridge", "council": "Redbridge Council", "neighbours": ["waltham-forest", "newham", "barking-and-dagenham", "havering"]},
    "richmond-upon-thames": {"id": 114, "name": "Richmond upon Thames", "council": "Richmond Council", "neighbours": ["hounslow", "kingston-upon-thames", "wandsworth", "hammersmith-and-fulham"]},
    "southwark": {"id": 115, "name": "Southwark", "council": "Southwark Council", "neighbours": ["lambeth", "lewisham", "city-of-london", "tower-hamlets"]},
    "sutton": {"id": 116, "name": "Sutton", "council": "Sutton Council", "neighbours": ["merton", "croydon", "kingston-upon-thames"]},
    "tower-hamlets": {"id": 117, "name": "Tower Hamlets", "council": "Tower Hamlets Council", "neighbours": ["hackney", "city-of-london", "newham", "greenwich", "southwark"]},
    "waltham-forest": {"id": 118, "name": "Waltham Forest", "council": "Waltham Forest Council", "neighbours": ["enfield", "haringey", "hackney", "redbridge", "newham"]},
    "wandsworth": {"id": 119, "name": "Wandsworth", "council": "Wandsworth Council", "neighbours": ["lambeth", "merton", "richmond-upon-thames", "hammersmith-and-fulham", "kingston-upon-thames"]},
    "westminster": {"id": 120, "name": "Westminster", "council": "Westminster City Council", "neighbours": ["camden", "kensington-and-chelsea", "city-of-london", "brent", "lambeth"]},
}

# H1/title use the display name without "the" prefix tricks: "Food hygiene
# ratings in the City of London" reads correctly because the name embeds it.
