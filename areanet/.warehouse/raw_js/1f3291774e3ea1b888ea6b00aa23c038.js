<!DOCTYPE html>
<html lang="en">
<head>
    <title>Hall of Monuments Reward Calculator</title>
    <meta charset="utf-8">
    <meta name="Language" content="en" />
    <link type="text/plain" rel="author" href="/humans.txt" />

    <link rel="stylesheet" href="https://2hom.staticwars.com/css/fonts.65b12463.css" />

    <link rel="stylesheet" href="https://static.staticwars.com/combo/_/fonts/cronos/v1/cronos-regular-min.css&/yui/3.2.0/cssfonts/fonts-min.css&/yui/3.2.0/cssreset/reset-min.css&/yui/3.2.0/cssgrids/grids-min.css&/yui/3.2.0/assets/skins/sam/overlay-min.css&/yui/3.2.0/assets/skins/sam/widget-min.css&/yui/3.2.0/assets/skins/sam/widget-stack-min.css">
<link rel="stylesheet" href="https://2hom.staticwars.com/css/hom.133df1c7.css" id="hom-css"/>

    <link rel="stylesheet" href="https://static.staticwars.com/bumpers/5/index.min.css" />

    <link rel="preload" as="image" href="https://2hom.staticwars.com/img/header-icon.980fa9eb.png">
</head>
<body lang="en" class="hom-flex">


    <div data-mount="anetdimebar"></div>

    <div id="hd">
        <div class="inner">
            <div class="bd-width">
                <a href="http://www.guildwars2.com/en/" id="logo" class="hide-txt">
                    Guild Wars 2
                </a>

                <a href="/" id="hom">
                    Hall of Monuments Reward Calculator
                </a>

                <form>
                    <h1 class="hide-txt">Hall of Monuments Reward Calculator</h1>

                    
                    <fieldset>
                        <p class="ib char">
                            <label for="char-name">Enter character name</label>
                            <input type="text" placeholder="Enter character name" id="char-name" />
                        </p>
                        <button type="submit" class="ib hide-txt">Go</button>
                    </fieldset>
                    
                </form>


                <div class="social">
                    <h5>Spread the word</h5>
                    <ul>
                        <li class="ib facebook">
                            <a
                                href="http://www.facebook.com/sharer.php?u=http://hom.guildwars2.com&amp;t=Hall of Monuments Reward Calculator"
                                class="hide-txt external"
                                title="Share on Facebook"
                            >
                                Share on Facebook
                            </a>
                        </li>
                        <li class="ib reddit">
                            <a
                                href="http://reddit.com/submit?url=http://hom.guildwars2.com"
                                class="hide-txt external"
                                title="Share on Reddit"
                            >
                                Share on Reddit
                            </a>
                        </li>
                        <li class="ib twitter">
                            <a
                                href="http://twitter.com/share?text=Checking out the Guild Wars Hall of Monuments Reward Calculator&amp;url=http://hom.guildwars2.com"
                                class="hide-txt external"
                                title="Share on Twitter"
                            >
                                Share on Twitter
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    <div id="char-error" class="hide outlined default">
        <div class="bd">
            <h5 class="default">Error Loading Character</h5>
            <h5 class="no-data">Error Retrieving Character</h5>
            <h5 class="lose-todo">Watch out!</h5>
            <p class="default">We couldn&#x27;t load that character, please check your spelling.</p>
            <p class="no-data">Please sign that character in &amp;amp; out of the game to ensure we have data.</p>
            <p class="lose-todo">A new search will erase your &#x27;to do&#x27; list! Please ensure you have saved it.</p>
        </div>
    </div>


<div id="bd" class="welcome">

    <div id="welcome">
        <div class="bd-width">
            <div class="bd">
                <h2>Discover Your Legacy in the Hall of Monuments</h2>
                <h3>Enter your Guild Wars<sup>&reg;</sup> character name to see what rewards you've earned for Guild Wars 2</h3>
                <p>Earn special <em>Guild Wars 2</em> rewards based on your achievements in the original <em>Guild Wars</em> and <em>Guild Wars: Eye of the North™</em>. Use the Hall of Monuments Reward Calculator to determine what rewards you've unlocked, how the benefits are calculated, and what other items are available.</p>
                <p>Just enter your <em>Guild Wars</em> character name in the field above to get started! If you don't have a character name to use, you can still access the Reward Calculator in <a href='#page=main&amp;details=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'>demo mode</a></p>

                <h4>Create Your Guild Wars Legend</h4>
                <p><em>Guild Wars 2</em> rewards are based on the achievements and honors accumulated by your <em>Guild Wars</em> character in the Hall of Monuments, which is only available in <em>Guild Wars: Eye of the North</em>. Check out our <a href="/en/faq/">FAQ</a> for more details. Pick up your copy of <em>Eye of the North</em> today and begin forging your legacy!</p>

                <h4>Spread the Word</h4>
                <p>Link your Hall of Monuments rewards on your favorite social networking sites and bask in the admiration of your friends!</p>

                <h4>Hall of Monuments now supports the Steam Ecosystem!</h4>
                <p>Players that use Steam logins for both Guild Wars Reforged and Guild Wars 2 automatically have their accounts connected and can begin unlocking Hall of Monuments rewards. Note that having Guild Wars in your Steam library is not the same thing as logging into Guild Wars with your Steam account. ArenaNet accounts and Steam accounts do not support cross-linking at this time.</p>
            </div>
        </div>
    </div>

    <div id="monitor"></div>
    <div id="main"></div>
    <div id="details"></div>
    <div id="print"></div>
</div>

<div id="overlays">
    <div id="meter-overlay" class="outlined hide">
        <div class="bd">
            <ul class="ib">
            </ul>

            <h6 class="ib cronos-reg"></h6>
        </div>
    </div>

    <div id="meter-overlay-container" class="bd-width"></div>

    <div id="item-overlay" class="hide">
        <div class="content">
            <div class="bd">
                <p class="count cronos-reg"></p>
                <ul></ul>
                <a href="#close" class="close hide-txt" title="Close">Close</a>
            </div>

            <a href="#prev" class="prev hide-txt nav" title="Previous Reward">Previous Reward</a>
            <a href="#next" class="next hide-txt nav" title="Next Reward">Next Reward</a>
        </div>
    </div>
</div>

<script>
    var HOM = {
    "lang": "en",
    "character": {
        "devotion": {
            "Common": 0,
            "Uncommon": 0,
            "Rare": 0,
            "Unique": 0
        },
        "fellowship": {
            "Zenmai": 0,
            "Norgu": 0,
            "Goren": 0,
            "Zhed Shadowhoof": 0,
            "General Morgahn": 0,
            "Margrid the Sly": 0,
            "Tahlkora": 0,
            "Razah": 0,
            "Master of Whispers": 0,
            "Koss": 0,
            "Dunkoro": 0,
            "Melonni": 0,
            "Acolyte Jin": 0,
            "Acolyte Sousuke": 0,
            "Vekk": 0,
            "Livia": 0,
            "Hayda": 0,
            "Ogden Stonehealer": 0,
            "Pyre Fierceshot": 0,
            "Jora": 0,
            "Kahmu": 0,
            "Xandra": 0,
            "Anton": 0,
            "Gwen": 0,
            "Animal Companion": 0,
            "Black Moa": 0,
            "Imperial Phoenix": 0,
            "Black Widow Spider": 0,
            "Olias": 0,
            "M.O.X.": 0
        },
        "honor": {
            "Eternal Champion": 0,
            "Eternal Commander": 0,
            "Eternal Skillz": 0,
            "Eternal Gladiator": 0,
            "Eternal Hero": 0,
            "Eternal Lightbringer": 0,
            "Eternal Bookah": 0,
            "Eternal Delver": 0,
            "Eternal Slayer": 0,
            "Eternal Ebon Vanguard Agent": 0,
            "Eternal Defender of Ascalon ": 0,
            "Eternal Tyrian Cartographer ": 0,
            "Eternal Guardian of Tyria": 0,
            "Eternal Protector of Tyria": 0,
            "Eternal Tyrian Skill Hunter": 0,
            "Eternal Tyrian Vanquisher": 0,
            "Eternal Canthan Cartographer ": 0,
            "Eternal Guardian of Cantha": 0,
            "Eternal Protector of Cantha": 0,
            "Eternal Canthan Skill Hunter": 0,
            "Eternal Canthan Vanquisher": 0,
            "Eternal Savior of the Kurzicks": 0,
            "Eternal Savior of the Luxons": 0,
            "Eternal Elonian Cartographer ": 0,
            "Eternal Guardian of Elona": 0,
            "Eternal Protector of Elona": 0,
            "Eternal Elonian Skill Hunter": 0,
            "Eternal Elonian Vanquisher": 0,
            "Eternal Ale-Hound": 0,
            "Eternal Party Animal": 0,
            "Eternal Master of the North": 0,
            "Eternal Legendary Cartographer ": 0,
            "Eternal Legendary Guardian": 0,
            "Eternal Legendary Skill Hunter": 0,
            "Eternal Legendary Vanquisher": 0,
            "Eternal Fortune": 0,
            "Eternal Sweet Tooth": 0,
            "Eternal Spearmarshal": 0,
            "Eternal Survivor": 0,
            "": 0,
            "Eternal Treasure Hunter": 0,
            "Eternal Misfortune": 0,
            "Eternal Source of Wisdom": 0,
            "Eternal Hero of Tyria": 0,
            "Eternal Hero of Cantha": 0,
            "Eternal Hero of Elona": 0,
            "Eternal Conqueror of Sorrow's Furnace": 0,
            "Eternal Conqueror of the Deep": 0,
            "Eternal Conqueror of Urgoz's Warren": 0,
            "Eternal Conqueror of the Fissure of Woe": 0,
            "Eternal Conqueror of the Underworld": 0,
            "Eternal Conqueror of the Domain of Anguish": 0,
            "Eternal Zaishen Supporter": 0,
            "Eternal Codex Disciple": 0
        },
        "resilience": {
            "Elite Canthan Armor": 0,
            "Elite Exotic Armor": 0,
            "Elite Kurzick Armor": 0,
            "Elite Luxon Armor": 0,
            "Imperial Ascended Armor": 0,
            "Ancient Armor": 0,
            "Elite Sunspear Armor": 0,
            "Vabbian Armor": 0,
            "Primeval Armor": 0,
            "Asuran Armor": 0,
            "Norn Armor": 0,
            "Silver Eagle Armor": 0,
            "Monument Armor": 0,
            "Obsidian Armor": 0,
            "Granite Citadel Elite Armor": 0,
            "Granite Citadel Exclusive Armor": 0,
            "Granite Citadel Ascended Armor": 0,
            "Marhan's Grotto Elite Armor": 0,
            "Marhan's Grotto Exclusive Armor": 0,
            "Marhan's Grotto Ascended Armor": 0
        },
        "valor": {
            "Destroyer Axe": 0,
            "Destroyer Bow": 0,
            "Destroyer Daggers": 0,
            "Destroyer Focus": 0,
            "Destroyer Maul": 0,
            "Destroyer Scepter": 0,
            "Destroyer Scythe": 0,
            "Destroyer Shield": 0,
            "Destroyer Spear": 0,
            "Destroyer Staff": 0,
            "Destroyer Sword": 0,
            "Tormented Axe": 0,
            "Tormented Bow": 0,
            "Tormented Daggers": 0,
            "Tormented Focus": 0,
            "Tormented Maul": 0,
            "Tormented Scepter": 0,
            "Tormented Scythe": 0,
            "Tormented Shield": 0,
            "Tormented Spear": 0,
            "Tormented Staff": 0,
            "Tormented Sword": 0,
            "Oppressor Axe": 0,
            "Oppressor Bow": 0,
            "Oppressor Daggers": 0,
            "Oppressor Focus": 0,
            "Oppressor Maul": 0,
            "Oppressor Scepter": 0,
            "Oppressor Scythe": 0,
            "Oppressor Shield": 0,
            "Oppressor Spear": 0,
            "Oppressor Staff": 0,
            "Oppressor Sword": 0
        }
    },
    "rewards": {
        "regular": [
            {
                "name": "Heritage Shoes, Boots, Warboots",
                "desc": "Heritage footwear for light, medium, and heavy armor professions",
                "ldesc": "Heritage footwear that evokes the majesty of bygone days for light, medium, and heavy armor professions."
            },
            {
                "name": "Heritage Pants, Legguards, Legplates",
                "desc": "Heritage legwear for light, medium, and heavy armor professions",
                "ldesc": "Heritage legwear that give your Guild Wars 2 character a classic look whether they wear light, medium, or heavy armor."
            },
            {
                "name": "Heritage Great Coat, Jerkin, Warplate",
                "desc": "Heritage coats for light, medium, and heavy armor professions",
                "ldesc": "Vintage Tyrian clothing with different designs for light, medium, and heavy armor professions."
            },
            {
                "name": "Heritage Gloves, Armguards, Gauntlets",
                "desc": "Heritage handwear for light, medium, and heavy armor professions",
                "ldesc": "Legacy gloves from Tyrian history designed for light, medium, and heavy armor professions."
            },
            {
                "name": "Heritage Mantle, Shoulderpads, Pauldrons",
                "desc": "Heritage shoulder covering for light, medium, and heavy armor professions",
                "ldesc": "Pieces of shoulder armor that recall centuries past, designed for light, medium, and heavy armor professions."
            },
            {
                "name": "Heritage Masque, Bandana, Warhelm",
                "desc": "Heritage headwear for light, medium, and heavy armor professions",
                "ldesc": "Headwear from Tyrian history for light, medium, and heavy armor professions."
            },
            {
                "name": "Gnarled Walking Stick",
                "desc": "An ancient staff",
                "ldesc": "A gnarled old staff that glows with ancient power."
            },
            {
                "name": "Living Shortbow",
                "desc": "An organic bow",
                "ldesc": "A vine-wrapped living weapon."
            },
            {
                "name": "Orange Tabby Cat",
                "desc": "A feline mini-pet",
                "ldesc": "An orange cat mini-pet that will keep your &lt;em>Guild Wars 2&lt;/em> character company."
            },
            {
                "name": "Fiery Dragon Sword",
                "desc": "A flaming dragon blade",
                "ldesc": "A stylized fire-breathing dragon sword."
            },
            {
                "name": "Diamond Aegis",
                "desc": "A brilliant diamond shield",
                "ldesc": "A dazzling diamond defense."
            },
            {
                "name": "Baroque Mask",
                "desc": "An elegant harlequin mask",
                "ldesc": "A baroque mask that recalls the festivals of old."
            },
            {
                "name": "Centurion's Claw",
                "desc": "A double-bladed dagger",
                "ldesc": "A deadly double-bladed dagger worthy of a charr centurion."
            },
            {
                "name": "Wheelock Rifle",
                "desc": "An antique rifle",
                "ldesc": "A vintage, handcrafted rifle that still packs a punch."
            },
            [
                {
                    "name": "Orrian Baby Chicken",
                    "desc": "An oddly lovable mini-pet",
                    "ldesc": "A creepy, cute little bird mini-pet from corrupted Orr."
                },
                {
                    "name": "Black Moa",
                    "desc": "A dark-feathered moa for rangers",
                    "ldesc": "A dark-feathered moa animal companion for your ranger."
                }
            ],
            {
                "name": "Wayward Wand",
                "desc": "A clawed scepter",
                "ldesc": "A clawed wand that pulses with power. "
            },
            {
                "name": "Seathunder Pistol",
                "desc": "An aquatic themed pistol",
                "ldesc": "An aquatic pistol with a fishy look."
            },
            {
                "name": "Heavenly Bracers",
                "desc": "Gauntlets of Dwayna",
                "ldesc": "Bracers that bear the visage of the human goddess Dwayna."
            },
            {
                "name": "Deldrimor Mace",
                "desc": "An ancient dwarven mace",
                "ldesc": "A dwarven weapon forged in the ancient kingdom of Deldrimor."
            },
            [
                {
                    "name": "Chimeric Prism",
                    "desc": "A brilliant, colorful focus",
                    "ldesc": "A colorful focus for your spellcaster."
                },
                {
                    "name": "Rainbow Jellyfish",
                    "desc": "A spineless aquatic companion for your ranger",
                    "ldesc": "A luminous, multi-colored jellyfish animal companion for your ranger."
                }
            ],
            {
                "name": "Rockfur Raccoon",
                "desc": "A woodland mini-pet",
                "ldesc": "A rascally raccoon minipet for your Guild Wars 2 character."
            },
            {
                "name": "Ithas Longbow",
                "desc": "A legendary longbow",
                "ldesc": "A bow just like the famed longbow wielded by the hero Lieutenant Thackeray during the Krytan Civil War."
            },
            {
                "name": "Fellblade",
                "desc": "An ominous greatsword",
                "ldesc": "An ominous, intimidating greatsword."
            },
            {
                "name": "Icelord's Diadem",
                "desc": "An icy crown",
                "ldesc": "A mystical icy crown that won't give you a cold headache."
            },
            [
                {
                    "name": "Ice Breaker",
                    "desc": "A mighty hammer of ice",
                    "ldesc": "A gleaming mallet of indestructible ice."
                },
                {
                    "name": "White Raven Skin",
                    "desc": "A white-feathered raven for your ranger",
                    "ldesc": "A rare albino raven animal companion for your ranger."
                }
            ],
            {
                "name": "Flaming Beacon",
                "desc": "An eternally burning torch",
                "ldesc": "A blazing, stylized torch whose flame never falters."
            },
            {
                "name": "Red Servitor Golem",
                "desc": "A loyal golem mini-pet",
                "ldesc": "A golem mini-pet that will happily tag along with you &mdash; just don't expect him to fight!"
            },
            {
                "name": "Stygian Reaver",
                "desc": "A long sought-after axe",
                "ldesc": "An extremely rare axe of impressive power."
            },
            {
                "name": "Mountaincall Warhorn",
                "desc": "A great horn from antiquity",
                "ldesc": "A fabled horn that recalls the glory of the lost human kingdom of Ascalon."
            },
            [
                {
                    "name": "Fire God's Vambraces",
                    "desc": "Fiery gloves of the human god Balthazar",
                    "ldesc": "A set of flaming bracers that bear the image of Balthazar, human god of fire and war."
                },
                {
                    "name": "Black Widow Spider",
                    "desc": "A deadly spider companion for your ranger",
                    "ldesc": "A sinister spider animal companion for your ranger."
                }
            ]
        ],
        "special": {
            "partial": {
                "name": "All reward items unlocked!",
                "desc": "Ready to really test yourself? Unlock the remaining titles to secure your place in Tyrian history!"
            },
            "max": {
                "name": "M-M-M-M-M-MONSTER KILL!",
                "desc": "Seriously, you crazy."
            }
        }
    },
    "titles": {
        "5": "Traveler",
        "10": "Guild Warrior",
        "15": "Rift Warden",
        "20": "Chosen",
        "25": "Ascendant",
        "30": "Closer to the Stars",
        "35": "Ghostly Hero",
        "40": "Flameseeker",
        "45": "Legend of the Mists",
        "50": "Champion of the Gods",
        "desc": "Reward Title"
    },
    "cols": {
        "order": [
            "devotion",
            "fellowship",
            "honor",
            "resilience",
            "valor"
        ],
        "details": {
            "devotion": {
                "title": "Devotion",
                "btn": "View Minipets",
                "total": 8
            },
            "fellowship": {
                "title": "Fellowship",
                "btn": "View Heroes & Pets",
                "total": 8
            },
            "honor": {
                "title": "Honor",
                "btn": "View Titles",
                "total": 18
            },
            "resilience": {
                "title": "Resilience",
                "btn": "View Armor",
                "total": 8
            },
            "valor": {
                "title": "Valor",
                "btn": "View Weapons",
                "total": 8
            }
        }
    },
    "urls": {
        "wiki": {
            "_base": "http://wiki.guildwars.com/wiki/",
            "resilience": "%22Resilience%22#Statues",
            "devotion": "%22Devotion%22",
            "fellowship": "%22Fellowship%22",
            "honor": "%22Honor%22",
            "valor": "%22Valor%22#Gallery"
        },
        "sharing": {
            "Twitter": "http://twitter.com/share?text={text}&url={url}",
            "Facebook": "http://www.facebook.com/sharer.php?t={text}&u={url}"
        }
    },
    "rules": {
        "items": {
            "fellowship": {
                "rare": [
                    "Black Moa",
                    "Imperial Phoenix",
                    "Black Widow Spider"
                ],
                "pet": [
                    "Animal Companion"
                ]
            },
            "honor": {
                "codex_commander": [
                    "Eternal Commander",
                    "Eternal Codex Disciple"
                ],
                "pvp": [
                    "Eternal Hero",
                    "Eternal Champion",
                    "Eternal Gladiator",
                    "Eternal Zaishen Supporter"
                ]
            },
            "resilience": {
                "vabbian": [
                    "Vabbian Armor"
                ],
                "obsidian": [
                    "Obsidian Armor"
                ],
                "kurzick_luxon": [
                    "Elite Luxon Armor",
                    "Elite Kurzick Armor"
                ]
            },
            "valor": {
                "destroyer": [
                    "Destroyer Axe",
                    "Destroyer Bow",
                    "Destroyer Daggers",
                    "Destroyer Focus",
                    "Destroyer Maul",
                    "Destroyer Scepter",
                    "Destroyer Scythe",
                    "Destroyer Shield",
                    "Destroyer Spear",
                    "Destroyer Staff",
                    "Destroyer Sword"
                ],
                "tormented": [
                    "Tormented Axe",
                    "Tormented Bow",
                    "Tormented Daggers",
                    "Tormented Focus",
                    "Tormented Maul",
                    "Tormented Scepter",
                    "Tormented Scythe",
                    "Tormented Shield",
                    "Tormented Spear",
                    "Tormented Staff",
                    "Tormented Sword"
                ],
                "oppressor": [
                    "Oppressor Axe",
                    "Oppressor Bow",
                    "Oppressor Daggers",
                    "Oppressor Focus",
                    "Oppressor Maul",
                    "Oppressor Scepter",
                    "Oppressor Scythe",
                    "Oppressor Shield",
                    "Oppressor Spear",
                    "Oppressor Staff",
                    "Oppressor Sword"
                ]
            }
        },
        "rules": {
            "valor": [
                "Any Weapon Statue",
                "Destroyer Weapon Statue",
                "Tormented Weapon Statue",
                "Oppressor Weapon Statue",
                "5 Weapon Statues",
                "11 Weapon Statues (Full Display)",
                "15 Weapon Statues"
            ],
            "honor": [
                "Accounts Linked",
                "Any Statue",
                "1 PvP Statue",
                "5 Statues (Full Display)",
                "10 Statues",
                "15 Statues",
                "20 Statues",
                "25 Statues",
                "30 Statues",
                "35 Statues",
                "40 Statues"
            ],
            "devotion": [
                "Any Miniature Statue",
                "Rare Miniature Statue",
                "Unique Miniature Statue",
                "20 Miniature Statues",
                "30 Miniature Statues",
                "40 Miniature Statues",
                "50 Miniature Statues"
            ],
            "fellowship": [
                "Any Hero Statue",
                "Any Pet Statue",
                "Any Rare Pet Statue",
                "5 Companion Statues (Full Display)",
                "10 Companion Statues",
                "20 Companion Statues",
                "30 Companion Statues"
            ],
            "resilience": [
                "Any Armor Statue",
                "3 Armor Statues",
                "5 Armor Statues (Full display)",
                "7 Armor Statues",
                "Kurzick or Luxon Armor Statue",
                "Vabbian Armor Statue",
                "Obsidian Armor Statue"
            ]
        }
    },
    "strings": {
        "details": {
            "BackButton": "&laquo; Back to overview",
            "WikiLink": "Wiki Article",
            "MyItems": "My Collection",
            "UnobtainedItems": "Unobtained Items"
        },
        "faq": {
            "Header": "Hall of Monuments FAQ",
            "InGameAccessQ": "Q: How do you access the Hall of Monuments in-game?",
            "InGameAccessA": "A: The Hall of Monuments is only available to players who have the <em>Guild Wars: Eye of the North</em> expansion. Once a <em>Guild Wars</em> character has reached level 10, they can speak to an NPC who will give them a quest:",
            "InGameAccessProphecies": "<em>Prophecies</em> characters can speak to <a href=\"https://wiki.guildwars.com/wiki/Len_Caldoron\" title=\"Len Caldoron\">Len Caldoron</a> in <a href=\"https://wiki.guildwars.com/wiki/Lion%27s_Arch\" title=\"Lion's Arch\">Lion's Arch</a>.",
            "InGameAccessFactions": "<em>Factions </em> characters can speak to <a href=\"https://wiki.guildwars.com/wiki/Minister_of_Maintenance_Raiugyon\" title=\"Minister of Maintenance Raiugyon\"> Minister of Maintenance Raiugyon</a> in <a href=\"https://wiki.guildwars.com/wiki/Kaineng_Center\" title=\"Kaineng Center\">Kaineng Center</a>.",
            "InGameAccessNightfall": "<em>Nightfall</em> characters can speak to <a href=\"https://wiki.guildwars.com/wiki/Bendah\" title=\"Bendah\">Bendah</a> in <a href=\"https://wiki.guildwars.com/wiki/Kamadan\" title=\"Kamadan\">Kamadan</a>.",
            "InGameAccessFinal": "This quest will send characters to the Eye of the North outpost, which is where they can enter the Hall of Monuments.",
            "MonumentUnlockQ": "Q: How do I unlock the Monuments of Devotion, Fellowship, Resilience, and Valor in game?",
            "MonumentUnlockA": "A: As you are completing the primary quest line in <em>Eye of the North</em>, your character will receive Monumental Tapestries, which let you choose which of the side monuments (Devotion, Fellowship, etc.) you want to unlock for any given character. The main Monument of Honor does not require the use of a Monumental Tapestry to unlock.",
            "AccountVsCharacterQ": "Q: How do I view the account version of the Hall of Monuments in-game instead of the character version?",
            "AccountVsCharacterA": "A: When entering the Hall of Monuments in-game you can speak to <a href=\"https://wiki.guildwars.com/wiki/Kimmes_The_Historian\">Kimmes the Historian</a>, who will show you the account version of your Hall of Monuments, which shows all the monuments and statues you have unlocked across all characters on your account, rather than just a specific character's monument and statue unlocks.",
            "GwammQ": "Q: Do players who obtained the title God Walking Amongst Mere Mortals in <em>Guild Wars</em> get anything special in <em>Guild Wars 2</em>?",
            "GwammA": "A: Yes, the maximum rank of the God Walking Amongst Mere Mortals title will be paid forward into <em>Guild Wars 2</em>. If you have earned this title on <em>any</em> of your Guild Wars characters, you will be able to have any of your <em>Guild Wars 2</em> characters wear the title as well. GWAMM is completely separate from the rewards that you can see via the Hall of Monuments Reward Calculator.",
            "PvpQ": "Q: Which titles count as a PvP title for the purposes of the Monument of Honor?",
            "PvpA": "A: Champion, Codex, Commander, Gladiator, Hero, and Zaishen titles all count towards the bonus you earn for having unlocked a PvP statue in the Hall of Monuments. The now defunct Commander title is now treated the same as having the Codex title, so if you already have one of those titles there's no need to get the other.",
            "TitlesQ": "Q: How do the Reward Titles work? Will I be able to choose from the ones I've earned, or will it only display my highest rank?",
            "TitlesA": "A: Each of the titles earned through the Hall of Monuments is a separate title, so you can choose which of them you want to wear on any given character in <em>Guild Wars 2</em>.",
            "CharacterVsAccountQ": "Q: Are the achievements on the Reward Calculator based on a specific Guild Wars character or based on all characters in the entire Guild Wars account?",
            "CharacterVsAccountA": "A: Everything found on the Reward Calculator is account-based. While you may enter a single character's name into the Reward Calculator, it still displays the cumulative achievements of all characters on that account.",
            "TodoAddQ": "Q: How do you add items to the \"to-do list\" in the Hall of Monuments Reward Calculator?",
            "TodoAddA": "A: You can hover over unobtained items on the list, and hit the plus sign to add them to your to-do list. You can then view and print off this list by selecting the print option.",
            "SellTradeQ": "Q: Will I be able to sell or trade my rewards in <em>Guild Wars 2</em>?",
            "SellTradeA": "A: No, you won't be able to trade any of the Hall of Monuments items or rewards to other accounts. You can, however, generate as many of the items as you want for your own account, so all of your <em>Guild Wars 2</em> characters can benefit from the rewards.",
            "ContinuingRewardsQ": "Q: Will I be able to continue earning Hall of Monuments rewards in <em>Guild Wars</em> after <em>Guild Wars 2</em> is released?",
            "ContinuingRewardsA": "A: Yes.",
            "AccountsLinkedQ": "Q: Why did I receive 3 points for having &quot;Accounts Linked&quot; under the Monument of Honor when I haven't done any linking yet?",
            "AccountsLinkedA": "A: When <em>Guild Wars 2</em> is released, there will be a way to link your <em>Guild Wars</em> account to your <em>Guild Wars 2</em> account.  If you own <em>Eye of the North</em>, you will receive 3 points for linking the accounts together.  The Reward Calculator assumes that you will have linked the accounts together, so it automatically gives you those points.",
            "GWCharGW2Q": "Q: Do we have to use our Guild Wars character name in Guild Wars 2 in order to receive Hall of Monuments benefits?",
            "GWCharGW2A": "A: You don't need to use your Guild Wars character name in order to benefit from the Hall of Monuments rewards in Guild Wars 2.  Use whatever name you like in Guild Wars 2!",
            "GWMultipleQ": "Q: Will we have the ability to link multiple Guild Wars accounts to a single Guild Wars 2 account?",
            "GWMultipleA": "A: No, only one Guild Wars account can be linked to a Guild Wars 2 account.  Furthermore, a single Guild Wars account can only be linked once to a single Guild Wars 2 account.",
            "RecentUpdatesQ": "Q: Why can't I see my most recent updates to the Hall of Monuments in the Rewards Calculator?",
            "RecentUpdatesA": "A: After updating your Hall of Monuments with new statues, you must log out of Guild Wars in order for the changes to appear in the Reward Calculator.",
            "AnimalCompanionsQ": "Q: Which animal companions are eligible for registering in the Hall of Monuments?",
            "AnimalCompanionsA": "A: Only the <a href=\"https://wiki.guildwars.com/wiki/Black_Moa\">Black Moa</a>, <a href=\"https://wiki.guildwars.com/wiki/Black_Widow\">Black Widow</a>, and <a href=\"https://wiki.guildwars.com/wiki/Phoenix_%28pet%29\">Imperial Phoenix</a> have their own unique statues on the Monument of Fellowship.  There is a general Animal Companion statue which can be unlocked with any level 20 evolved pet, such as the <a href=\"https://wiki.guildwars.com/wiki/Rainbow_phoenix\">Rainbow Phoenix</a>.  This Animal Companion statue can only be unlocked once per character, and you only need to unlock it once on your account for the purposes of the Hall of Monument rewards.",
            "MiniaturesDupesQ": "Q: How do I add miniatures to the Hall of Monuments and avoid registering the same miniature that another character has already added?",
            "MiniaturesDupesA": "A: You can dedicate miniatures in your inventory by interacting with the <a href=\"https://wiki.guildwars.com/wiki/%22Devotion%22\">Monument of Devotion</a> in-game.  You can't add miniatures which already say \"Dedicated at Hall of Monuments\" in their item description, because that means that miniature has already been dedicated.  The easiest way to see if you already have a miniature dedicated in your account collection is by speaking to <a href=\"https://wiki.guildwars.com/wiki/Kimmes_The_Historian\">Kimmes the Historian</a> at the entrance of the Hall of Monuments.  Ask him to show your account accomplishments instead of your character's accomplishment, and then return to the Monument of Devotion to see all the miniatures on your entire account.",
            "MissingCreditQ": "Q: Why doesn't the Reward Calculator say I have credit for something I know I have achieved?",
            "MissingCreditA": "A: The Reward Calculator only shows you things which have been registered at the actual <a href=\"https://wiki.guildwars.com/wiki/Hall_of_Monuments\">Hall of Monuments</a>, so you must go there in-game and interact with the monument associated with the item or other achievement you have earned.",
            "MissingCreditMinis": "Miniatures are registered at the <a href=\"https://wiki.guildwars.com/wiki/%22Devotion%22\">Monument of Devotion</a>.",
            "MissingCreditHeroes": "Heroes and animal companions are registered at the <a href=\"https://wiki.guildwars.com/wiki/%22Fellowship%22\">Monument of Fellowship</a>.",
            "MissingCreditTitles": "Titles and other special achievements are registered at the <a href=\"https://wiki.guildwars.com/wiki/%22Honor%22\">Monument of Honor</a>.",
            "MissingCreditArmor": "Armor is registered at the <a href=\"https://wiki.guildwars.com/wiki/%22Resilience%22\">Monument of Resilience</a>.",
            "MissingCreditWeapons": "Weapons are registered at the <a href=\"https://wiki.guildwars.com/wiki/%22Valor%22\">Monument of Valor</a>.",
            "UnableToRegisterQ": "Q: Why can't I register a particular item in my Hall of Monuments?",
            "UnableToRegisterA1": "A: First, make sure that the appropriate monument has been unlocked on that character by interacting with it while you have a <a href=\"https://wiki.guildwars.com/wiki/Monumental_tapestry\">Monumental Tapestry</a> in your inventory.  If it still isn't letting you register an item, hero, or animal companion that you have brought along, then chances are you are in account mode at the Hall of Monuments and the actual character attempting to do the registering hasn't yet unlocked that monument.  If you think this may be happening to you, then try speaking with <a href=\"https://wiki.guildwars.com/wiki/Kimmes_The_Historian\">Kimmes the Historian</a> to verify that you are in fact viewing that character's unlocks, and not your account achievements.",
            "UnableToRegisterA2": "Here are some more troubleshooting tips if you are having difficulty unlocking any particular item:",
            "UnableToregisterMinis": "Miniatures must be in your inventory and undedicated, so make sure that the one you are trying to register doesn't already say \"Dedicated at Hall of Monuments\" on it.",
            "UnableToregisterAnimals": "Animal companions must be level 20, evolved, and charmed by your character in order to be registered, so make sure to have <a href=\"https://wiki.guildwars.com/wiki/Charm_Animal\">Charm Animal</a>, <a href=\"https://wiki.guildwars.com/wiki/Comfort_Animal\">Comfort Animal</a>, or <a href=\"https://wiki.guildwars.com/wiki/Heal_as_one\">Heal as One</a> on your skill bar before entering the Hall of Monuments.",
            "UnableToregisterHeroes": "Heroes must have their armor upgraded and be in your party in order to be registered.  The one exception to this is <a href=\"https://wiki.guildwars.com/wiki/M.O.X.\">M.O.X.</a>, who can be added without armor upgrades.",
            "UnableToregisterTitles": "Titles need to be up to a certain rank before they can be registered, so make sure to cross-reference what your character has with the <a href=\"\">Monument of Honor</a> wiki page to see if it qualifies.",
            "UnableToregisterArmor": "You must be wearing an entire set of <a href=\"https://wiki.guildwars.com/wiki/Prestige_armor\">prestige armor</a> in order to register it.  A set consists of the chestpiece, gloves, leggings, and boots.  Headpieces are not required to register a set.",
            "UnableToregisterWeapons": "Weapons must be in your inventory and either <a href=\"https://wiki.guildwars.com/wiki/Customized\">customized</a> to the character wielding them, or uncustomized entirely at the time of registering.  In addition, only weapons from the <a href=\"https://wiki.guildwars.com/wiki/Category:Destroyer_weapons\">Destroyer</a>, <a href=\"https://wiki.guildwars.com/wiki/Category:Oppressor%27s_weapons\">Oppressor's</a>, and <a href=\"https://wiki.guildwars.com/wiki/Category:Tormented_weapons\">Tormented</a> sets can be registered. Weapons which were not customized at the time of registering will become customized to the character that registered it."
        },
        "header": {
            "GW2": "Guild Wars 2",
            "Title": "Hall of Monuments Reward Calculator",
            "SearchPlaceholder": "Enter character name",
            "ButtonGo": "Go",
            "SocialHd": "Spread the word",
            "ShareDelicious": "Share on Delicious",
            "ShareDigg": "Share on Digg",
            "ShareFacebook": "Share on Facebook",
            "ShareReddit": "Share on Reddit",
            "ShareTwitter": "Share on Twitter",
            "searchHdDefault": "Error Loading Character",
            "searchBdDefault": "We couldn't load that character, please check your spelling.",
            "searchHdNodata": "Error Retrieving Character",
            "searchBdNodata": "Please sign that character in &amp; out of the game to ensure we have data.",
            "searchHdLosetodo": "Watch out!",
            "searchBdLosetodo": "A new search will erase your 'to do' list! Please ensure you have saved it.",
            "Gw2Link": "http://www.guildwars2.com/en/"
        },
        "modal": {
            "Close": "Close",
            "Previous": "Previous Reward",
            "Next": "Next Reward"
        },
        "monitor": {
            "PrintButton": "Print",
            "PrintRewards": "Show Rewards",
            "PrintTodo": "Show 'To Do' List",
            "PrintCollection": "Show My Collection",
            "PrintUnobtained": "Show Unobtained",
            "ShareButton": "Save or Share",
            "ShareInstructions": "Click to Copy URL",
            "ShareSuccess": "Copied to clipboard",
            "ShareSubHead": "Or Share Using",
            "ShareTwitter": "Twitter",
            "ShareFacebook": "Facebook",
            "RewardMeter": "Reward Meter",
            "RewardPreview": "Preview 'to do' items in point calculation"
        },
        "print": {
            "Back": "« Back",
            "Print": "Print",
            "Points": "POINTS",
            "MyHOM": "My Hall of Monuments",
            "URL": "http://hom.guildwars2.com",
            "PointsHeader": "Point Breakdown",
            "Devotion": "Devotion",
            "Fellowship": "Fellowship",
            "Honor": "Honor",
            "Resilience": "Resilience",
            "Valor": "Valor",
            "RewardsHeader": "My Rewards",
            "TodoHeader": "'To Do' List",
            "CollectionHeader": "My Collection",
            "UnobtainedHeader": "Unobtained Items"
        },
        "welcome": {
            "Header": "Discover Your Legacy in the Hall of Monuments",
            "HeaderSub": "Enter your Guild Wars<sup>&reg;</sup> character name to see what rewards you've earned for Guild Wars 2",
            "HeaderPOne": "Earn special <em>Guild Wars 2</em> rewards based on your achievements in the original <em>Guild Wars</em> and <em>Guild Wars: Eye of the North™</em>. Use the Hall of Monuments Reward Calculator to determine what rewards you've unlocked, how the benefits are calculated, and what other items are available.",
            "HeaderPTwo": "Just enter your <em>Guild Wars</em> character name in the field above to get started! If you don't have a character name to use, you can still access the Reward Calculator in <a href='#page=main&amp;details=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'>demo mode</a>",
            "SubHeaderCreate": "Create Your Guild Wars Legend",
            "SubHeaderCreateP": "<em>Guild Wars 2</em> rewards are based on the achievements and honors accumulated by your <em>Guild Wars</em> character in the Hall of Monuments, which is only available in <em>Guild Wars: Eye of the North</em>. Check out our <a href=\"/en/faq/\">FAQ</a> for more details. Pick up your copy of <em>Eye of the North</em> today and begin forging your legacy!",
            "SubHeaderSpread": "Spread the Word",
            "SubHeaderSpreadP": "Link your Hall of Monuments rewards on your favorite social networking sites and bask in the admiration of your friends!",
            "SubHeaderSteam": "Hall of Monuments now supports the Steam Ecosystem!",
            "SubHeaderSteamP": "Players that use Steam logins for both Guild Wars Reforged and Guild Wars 2 automatically have their accounts connected and can begin unlocking Hall of Monuments rewards. Note that having Guild Wars in your Steam library is not the same thing as logging into Guild Wars with your Steam account. ArenaNet accounts and Steam accounts do not support cross-linking at this time.",
            "Footer": {
                "en": "US English",
                "de": "German",
                "fr": "French",
                "es": "Spanish"
            },
            "copyright": "©{year} ArenaNet, LLC. All rights reserved. All trademarks are the property of their respective owners."
        },
        "json_columns": {
            "DevotionTitle": "Devotion",
            "DevotionButton": "View Minipets",
            "FellowshipTitle": "Fellowship",
            "FellowshipButton": "View Heroes & Pets",
            "HonorTitle": "Honor",
            "HonorButton": "View Titles",
            "ResilienceTitle": "Resilience",
            "ResilienceButton": "View Armor",
            "ValorTitle": "Valor",
            "ValorButton": "View Weapons"
        },
        "json_titles": {
            "Description": "Reward Title",
            "5Title": "Traveler",
            "10Title": "Guild Warrior",
            "15Title": "Rift Warden",
            "20Title": "Chosen",
            "25Title": "Ascendant",
            "30Title": "Closer to the Stars",
            "35Title": "Ghostly Hero",
            "40Title": "Flameseeker",
            "45Title": "Legend of the Mists",
            "50Title": "Champion of the Gods"
        },
        "json_rewards": {
            "Reward01Name": "Heritage Shoes, Boots, Warboots",
            "Reward01Description": "Heritage footwear for light, medium, and heavy armor professions",
            "Reward01LongDescription": "Heritage footwear that evokes the majesty of bygone days for light, medium, and heavy armor professions.",
            "Reward02Name": "Heritage Pants, Legguards, Legplates",
            "Reward02Description": "Heritage legwear for light, medium, and heavy armor professions",
            "Reward02LongDescription": "Heritage legwear that give your Guild Wars 2 character a classic look whether they wear light, medium, or heavy armor.",
            "Reward03Name": "Heritage Great Coat, Jerkin, Warplate",
            "Reward03Description": "Heritage coats for light, medium, and heavy armor professions",
            "Reward03LongDescription": "Vintage Tyrian clothing with different designs for light, medium, and heavy armor professions.",
            "Reward04Name": "Heritage Gloves, Armguards, Gauntlets",
            "Reward04Description": "Heritage handwear for light, medium, and heavy armor professions",
            "Reward04LongDescription": "Legacy gloves from Tyrian history designed for light, medium, and heavy armor professions.",
            "Reward05Name": "Heritage Mantle, Shoulderpads, Pauldrons",
            "Reward05Description": "Heritage shoulder covering for light, medium, and heavy armor professions",
            "Reward05LongDescription": "Pieces of shoulder armor that recall centuries past, designed for light, medium, and heavy armor professions.",
            "Reward06Name": "Heritage Masque, Bandana, Warhelm",
            "Reward06Description": "Heritage headwear for light, medium, and heavy armor professions",
            "Reward06LongDescription": "Headwear from Tyrian history for light, medium, and heavy armor professions.",
            "Reward07Name": "Gnarled Walking Stick",
            "Reward07Description": "An ancient staff",
            "Reward07LongDescription": "A gnarled old staff that glows with ancient power.",
            "Reward08Name": "Living Shortbow",
            "Reward08Description": "An organic bow",
            "Reward08LongDescription": "A vine-wrapped living weapon.",
            "Reward09Name": "Orange Tabby Cat",
            "Reward09Description": "A feline mini-pet",
            "Reward09LongDescription": "An orange cat mini-pet that will keep your &lt;em>Guild Wars 2&lt;/em> character company.",
            "Reward10Name": "Fiery Dragon Sword",
            "Reward10Description": "A flaming dragon blade",
            "Reward10LongDescription": "A stylized fire-breathing dragon sword.",
            "Reward11Name": "Diamond Aegis",
            "Reward11Description": "A brilliant diamond shield",
            "Reward11LongDescription": "A dazzling diamond defense.",
            "Reward12Name": "Baroque Mask",
            "Reward12Description": "An elegant harlequin mask",
            "Reward12LongDescription": "A baroque mask that recalls the festivals of old.",
            "Reward13Name": "Centurion's Claw",
            "Reward13Description": "A double-bladed dagger",
            "Reward13LongDescription": "A deadly double-bladed dagger worthy of a charr centurion.",
            "Reward14Name": "Wheelock Rifle",
            "Reward14Description": "An antique rifle",
            "Reward14LongDescription": "A vintage, handcrafted rifle that still packs a punch.",
            "Reward15aName": "Orrian Baby Chicken",
            "Reward15aDescription": "An oddly lovable mini-pet",
            "Reward15aLongDescription": "A creepy, cute little bird mini-pet from corrupted Orr.",
            "Reward15bName": "Black Moa",
            "Reward15bDescription": "A dark-feathered moa for rangers",
            "Reward15bLongDescription": "A dark-feathered moa animal companion for your ranger.",
            "Reward16Name": "Wayward Wand",
            "Reward16Description": "A clawed scepter",
            "Reward16LongDescription": "A clawed wand that pulses with power. ",
            "Reward17Name": "Seathunder Pistol",
            "Reward17Description": "An aquatic themed pistol",
            "Reward17LongDescription": "An aquatic pistol with a fishy look.",
            "Reward18Name": "Heavenly Bracers",
            "Reward18Description": "Gauntlets of Dwayna",
            "Reward18LongDescription": "Bracers that bear the visage of the human goddess Dwayna.",
            "Reward19Name": "Deldrimor Mace",
            "Reward19Description": "An ancient dwarven mace",
            "Reward19LongDescription": "A dwarven weapon forged in the ancient kingdom of Deldrimor.",
            "Reward20aName": "Chimeric Prism",
            "Reward20aDescription": "A brilliant, colorful focus",
            "Reward20aLongDescription": "A colorful focus for your spellcaster.",
            "Reward20bName": "Rainbow Jellyfish",
            "Reward20bDescription": "A spineless aquatic companion for your ranger",
            "Reward20bLongDescription": "A luminous, multi-colored jellyfish animal companion for your ranger.",
            "Reward21Name": "Rockfur Raccoon",
            "Reward21Description": "A woodland mini-pet",
            "Reward21LongDescription": "A rascally raccoon minipet for your Guild Wars 2 character.",
            "Reward22Name": "Ithas Longbow",
            "Reward22Description": "A legendary longbow",
            "Reward22LongDescription": "A bow just like the famed longbow wielded by the hero Lieutenant Thackeray during the Krytan Civil War.",
            "Reward23Name": "Fellblade",
            "Reward23Description": "An ominous greatsword",
            "Reward23LongDescription": "An ominous, intimidating greatsword.",
            "Reward24Name": "Icelord's Diadem",
            "Reward24Description": "An icy crown",
            "Reward24LongDescription": "A mystical icy crown that won't give you a cold headache.",
            "Reward25aName": "Ice Breaker",
            "Reward25aDescription": "A mighty hammer of ice",
            "Reward25aLongDescription": "A gleaming mallet of indestructible ice.",
            "Reward25bName": "White Raven Skin",
            "Reward25bDescription": "A white-feathered raven for your ranger",
            "Reward25bLongDescription": "A rare albino raven animal companion for your ranger.",
            "Reward26Name": "Flaming Beacon",
            "Reward26Description": "An eternally burning torch",
            "Reward26LongDescription": "A blazing, stylized torch whose flame never falters.",
            "Reward27Name": "Red Servitor Golem",
            "Reward27Description": "A loyal golem mini-pet",
            "Reward27LongDescription": "A golem mini-pet that will happily tag along with you &mdash; just don't expect him to fight!",
            "Reward28Name": "Stygian Reaver",
            "Reward28Description": "A long sought-after axe",
            "Reward28LongDescription": "An extremely rare axe of impressive power.",
            "Reward29Name": "Mountaincall Warhorn",
            "Reward29Description": "A great horn from antiquity",
            "Reward29LongDescription": "A fabled horn that recalls the glory of the lost human kingdom of Ascalon.",
            "Reward30aName": "Fire God's Vambraces",
            "Reward30aDescription": "Fiery gloves of the human god Balthazar",
            "Reward30aLongDescription": "A set of flaming bracers that bear the image of Balthazar, human god of fire and war.",
            "Reward30bName": "Black Widow Spider",
            "Reward30bDescription": "A deadly spider companion for your ranger",
            "Reward30bLongDescription": "A sinister spider animal companion for your ranger.",
            "SpecialReward31Name": "All reward items unlocked!",
            "SpecialReward31Description": "Ready to really test yourself? Unlock the remaining titles to secure your place in Tyrian history!",
            "SpecialReward50Name": "M-M-M-M-M-MONSTER KILL!",
            "SpecialReward50Description": "Seriously, you crazy."
        },
        "json_points": {
            "common": "Common",
            "uncommon": "Uncommon",
            "rare": "Rare",
            "unique": "Unique",
            "Zenmai": "Zenmai",
            "Norgu": "Norgu",
            "Goren": "Goren",
            "ZhedShadowhoof": "Zhed Shadowhoof",
            "GeneralMorgahn": "General Morgahn",
            "MargridtheSly": "Margrid the Sly",
            "Tahlkora": "Tahlkora",
            "Razah": "Razah",
            "MasterofWhispers": "Master of Whispers",
            "Koss": "Koss",
            "Dunkoro": "Dunkoro",
            "Melonni": "Melonni",
            "AcolyteJin": "Acolyte Jin",
            "AcolyteSousuke": "Acolyte Sousuke",
            "Vekk": "Vekk",
            "Livia": "Livia",
            "Hayda": "Hayda",
            "OgdenStonehealer": "Ogden Stonehealer",
            "PyreFierceshot": "Pyre Fierceshot",
            "Jora": "Jora",
            "Kahmu": "Kahmu",
            "Xandra": "Xandra",
            "Anton": "Anton",
            "Gwen": "Gwen",
            "AnimalCompanion": "Animal Companion",
            "BlackMoa": "Black Moa",
            "ImperialPhoenix": "Imperial Phoenix",
            "BlackWidowSpider": "Black Widow Spider",
            "Olias": "Olias",
            "MOX": "M.O.X.",
            "EternalChampion": "Eternal Champion",
            "EternalCommander": "Eternal Commander",
            "EternalSkillz": "Eternal Skillz",
            "EternalGladiator": "Eternal Gladiator",
            "EternalHero": "Eternal Hero",
            "EternalLightbringer": "Eternal Lightbringer",
            "EternalBookah": "Eternal Bookah",
            "EternalDelver": "Eternal Delver",
            "EternalSlayer": "Eternal Slayer",
            "EternalEbonVanguardAgent": "Eternal Ebon Vanguard Agent",
            "EternalDefenderofAscalon": "Eternal Defender of Ascalon ",
            "EternalTyrianCartographer": "Eternal Tyrian Cartographer ",
            "EternalGuardianofTyria": "Eternal Guardian of Tyria",
            "EternalProtectorofTyria": "Eternal Protector of Tyria",
            "EternalTyrianSkillHunter": "Eternal Tyrian Skill Hunter",
            "EternalTyrianVanquisher": "Eternal Tyrian Vanquisher",
            "EternalCanthanCartographer": "Eternal Canthan Cartographer ",
            "EternalGuardianofCantha": "Eternal Guardian of Cantha",
            "EternalProtectorofCantha": "Eternal Protector of Cantha",
            "EternalCanthanSkillHunter": "Eternal Canthan Skill Hunter",
            "EternalCanthanVanquisher": "Eternal Canthan Vanquisher",
            "EternalSavioroftheKurzicks": "Eternal Savior of the Kurzicks",
            "EternalSavioroftheLuxons": "Eternal Savior of the Luxons",
            "EternalElonianCartographer": "Eternal Elonian Cartographer ",
            "EternalGuardianofElona": "Eternal Guardian of Elona",
            "EternalProtectorofElona": "Eternal Protector of Elona",
            "EternalElonianSkillHunter": "Eternal Elonian Skill Hunter",
            "EternalElonianVanquisher": "Eternal Elonian Vanquisher",
            "EternalAleHound": "Eternal Ale-Hound",
            "EternalPartyAnimal": "Eternal Party Animal",
            "EternalMasteroftheNorth": "Eternal Master of the North",
            "EternalLegendaryCartographer": "Eternal Legendary Cartographer ",
            "EternalLegendaryGuardian": "Eternal Legendary Guardian",
            "EternalLegendarySkillHunter": "Eternal Legendary Skill Hunter",
            "EternalLegendaryVanquisher": "Eternal Legendary Vanquisher",
            "EternalFortune": "Eternal Fortune",
            "EternalSweetTooth": "Eternal Sweet Tooth",
            "EternalSpearmarshal": "Eternal Spearmarshal",
            "EternalSurvivor": "Eternal Survivor",
            "EternalTreasureHunter": "Eternal Treasure Hunter",
            "EternalMisfortune": "Eternal Misfortune",
            "EternalSourceofWisdom": "Eternal Source of Wisdom",
            "EternalHeroofTyria": "Eternal Hero of Tyria",
            "EternalHeroofCantha": "Eternal Hero of Cantha",
            "EternalHeroofElona": "Eternal Hero of Elona",
            "EternalConquerorofSorrowsFurnace": "Eternal Conqueror of Sorrow's Furnace",
            "EternalConqueroroftheDeep": "Eternal Conqueror of the Deep",
            "EternalConquerorofUrgozsWarren": "Eternal Conqueror of Urgoz's Warren",
            "EternalConqueroroftheFissureofWoe": "Eternal Conqueror of the Fissure of Woe",
            "EternalConqueroroftheUnderworld": "Eternal Conqueror of the Underworld",
            "EternalConqueroroftheDomainofAnguish": "Eternal Conqueror of the Domain of Anguish",
            "EternalZaishenSupporter": "Eternal Zaishen Supporter",
            "EternalCodexDisciple": "Eternal Codex Disciple",
            "EliteCanthanArmor": "Elite Canthan Armor",
            "EliteExoticArmor": "Elite Exotic Armor",
            "EliteKurzickArmor": "Elite Kurzick Armor",
            "EliteLuxonArmor": "Elite Luxon Armor",
            "ImperialAscendedArmor": "Imperial Ascended Armor",
            "AncientArmor": "Ancient Armor",
            "EliteSunspearArmor": "Elite Sunspear Armor",
            "VabbianArmor": "Vabbian Armor",
            "PrimevalArmor": "Primeval Armor",
            "AsuranArmor": "Asuran Armor",
            "NornArmor": "Norn Armor",
            "SilverEagleArmor": "Silver Eagle Armor",
            "MonumentArmor": "Monument Armor",
            "ObsidianArmor": "Obsidian Armor",
            "GraniteCitadelEliteArmor": "Granite Citadel Elite Armor",
            "GraniteCitadelExclusiveArmor": "Granite Citadel Exclusive Armor",
            "GraniteCitadelAscendedArmor": "Granite Citadel Ascended Armor",
            "MarhansGrottoEliteArmor": "Marhan's Grotto Elite Armor",
            "MarhansGrottoExclusiveArmor": "Marhan's Grotto Exclusive Armor",
            "MarhansGrottoAscendedArmor": "Marhan's Grotto Ascended Armor",
            "DestroyerAxe": "Destroyer Axe",
            "DestroyerBow": "Destroyer Bow",
            "DestroyerDaggers": "Destroyer Daggers",
            "DestroyerFocus": "Destroyer Focus",
            "DestroyerMaul": "Destroyer Maul",
            "DestroyerScepter": "Destroyer Scepter",
            "DestroyerScythe": "Destroyer Scythe",
            "DestroyerShield": "Destroyer Shield",
            "DestroyerSpear": "Destroyer Spear",
            "DestroyerStaff": "Destroyer Staff",
            "DestroyerSword": "Destroyer Sword",
            "TormentedAxe": "Tormented Axe",
            "TormentedBow": "Tormented Bow",
            "TormentedDaggers": "Tormented Daggers",
            "TormentedFocus": "Tormented Focus",
            "TormentedMaul": "Tormented Maul",
            "TormentedScepter": "Tormented Scepter",
            "TormentedScythe": "Tormented Scythe",
            "TormentedShield": "Tormented Shield",
            "TormentedSpear": "Tormented Spear",
            "TormentedStaff": "Tormented Staff",
            "TormentedSword": "Tormented Sword",
            "OppressorAxe": "Oppressor Axe",
            "OppressorBow": "Oppressor Bow",
            "OppressorDaggers": "Oppressor Daggers",
            "OppressorFocus": "Oppressor Focus",
            "OppressorMaul": "Oppressor Maul",
            "OppressorScepter": "Oppressor Scepter",
            "OppressorScythe": "Oppressor Scythe",
            "OppressorShield": "Oppressor Shield",
            "OppressorSpear": "Oppressor Spear",
            "OppressorStaff": "Oppressor Staff",
            "OppressorSword": "Oppressor Sword"
        },
        "js": {
            "Minis": "{type} Miniatures",
            "TodoAdd": "Add to 'to do' list",
            "TodoDel": "Remove from 'to do' list",
            "TwitterText": "Checking out the Guild Wars Hall of Monuments Reward Calculator",
            "FacebookText": "Guild Wars Hall of Monuments Reward Calculator",
            "minis": {
                "common": "Common",
                "uncommon": "Uncommon",
                "rare": "Rare",
                "unique": "Unique"
            }
        },
        "json_rules": {
            "AnyWeaponStatue": "Any Weapon Statue",
            "DestroyerWeaponStatue": "Destroyer Weapon Statue",
            "TormentedWeaponStatue": "Tormented Weapon Statue",
            "OppressorWeaponStatue": "Oppressor Weapon Statue",
            "5WeaponStatues": "5 Weapon Statues",
            "11WeaponStatues(FullDisplay)": "11 Weapon Statues (Full Display)",
            "15WeaponStatues": "15 Weapon Statues",
            "AccountsLinked": "Accounts Linked",
            "AnyStatue": "Any Statue",
            "1PvPStatue": "1 PvP Statue",
            "5Statues(FullDisplay)": "5 Statues (Full Display)",
            "10Statues": "10 Statues",
            "15Statues": "15 Statues",
            "20Statues": "20 Statues",
            "25Statues": "25 Statues",
            "30Statues": "30 Statues",
            "35Statues": "35 Statues",
            "40Statues": "40 Statues",
            "AnyMiniatureStatue": "Any Miniature Statue",
            "RareMiniatureStatue": "Rare Miniature Statue",
            "UniqueMiniatureStatue": "Unique Miniature Statue",
            "20MiniatureStatues": "20 Miniature Statues",
            "30MiniatureStatues": "30 Miniature Statues",
            "40MiniatureStatues": "40 Miniature Statues",
            "50MiniatureStatues": "50 Miniature Statues",
            "AnyHeroStatue": "Any Hero Statue",
            "AnyPetStatue": "Any Pet Statue",
            "AnyRarePetStatue": "Any Rare Pet Statue",
            "5CompanionStatues(FullDisplay)": "5 Companion Statues (Full Display)",
            "10CompanionStatues": "10 Companion Statues",
            "20CompanionStatues": "20 Companion Statues",
            "30CompanionStatues": "30 Companion Statues",
            "AnyArmorStatue": "Any Armor Statue",
            "3ArmorStatues": "3 Armor Statues",
            "5ArmorStatues(Fulldisplay)": "5 Armor Statues (Full display)",
            "7ArmorStatues": "7 Armor Statues",
            "KurzickorLuxonArmorStatue": "Kurzick or Luxon Armor Statue",
            "VabbianArmorStatue": "Vabbian Armor Statue",
            "ObsidianArmorStatue": "Obsidian Armor Statue"
        }
    }
};
</script>
<script src="https://static.staticwars.com/combo/_/yui/3.2.0/_config-min.js&/yui/gallery/v4/_config-min.js&/yui/3.2.0/yui/yui-min.js&/yui/3.2.0/loader/loader-min.js"></script>
<script src="https://2hom.staticwars.com/combo/_/js/_config.d87bfc0d.js&/js/bootstrap.ba1bf3fe.js"></script>
<div data-mount="anetfooter"></div>

<!-- Google Tag Manager -->
<noscript><iframe src="//www.googletagmanager.com/ns.html?id=GTM-5ZJ94W"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'//www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-5ZJ94W');</script>
<!-- End Google Tag Manager -->

<script>
    window.anetFooterAttrs = {
        showNav     : true,
        noSocial    : true
    };
</script>

<script src="https://static.staticwars.com/bumpers/5/index.min.js"></script>

</body>
</html>

