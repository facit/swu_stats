BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "bases" (
	"base_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"set_number"	INTEGER,
	"aspect"	TEXT,
	"rarity"	TEXT,
	"nickname"	TEXT,
	PRIMARY KEY("base_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "cards" (
	"card_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"subtitle"	TEXT,
	"type"	TEXT NOT NULL,
	PRIMARY KEY("card_id"),
	UNIQUE("name","subtitle")
);
CREATE TABLE IF NOT EXISTS "deck_cards" (
	"deck_card_id"	INTEGER,
	"deck_id"	INTEGER,
	"card_id"	INTEGER,
	"count"	INTEGER,
	"sideboard"	INTEGER DEFAULT 0,
	PRIMARY KEY("deck_card_id"),
	FOREIGN KEY("card_id") REFERENCES "cards"("card_id"),
	FOREIGN KEY("deck_id") REFERENCES "decks"("deck_id")
);
CREATE TABLE IF NOT EXISTS "decks" (
	"deck_id"	INTEGER,
	"leader_id"	INTEGER NOT NULL,
	"base_id"	INTEGER NOT NULL,
	"decklink"	TEXT,
	PRIMARY KEY("deck_id" AUTOINCREMENT),
	FOREIGN KEY("base_id") REFERENCES "bases"("base_id"),
	FOREIGN KEY("leader_id") REFERENCES "leaders"("leader_id")
);
CREATE TABLE IF NOT EXISTS "leaders" (
	"leader_id"	INTEGER,
	"name"	TEXT,
	"subtitle"	TEXT,
	"set_number"	INTEGER,
	"nickname"	TEXT,
	"primary_aspect"	TEXT,
	"secondary_aspect"	TEXT,
	PRIMARY KEY("leader_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "player_aliases" (
	"alias_id"	INTEGER,
	"player_id"	INTEGER NOT NULL,
	"alias"	TEXT NOT NULL,
	PRIMARY KEY("alias_id"),
	UNIQUE("player_id","alias"),
	FOREIGN KEY("player_id") REFERENCES "players"("player_id")
);
CREATE TABLE IF NOT EXISTS "players" (
	"player_id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("player_id")
);
CREATE TABLE IF NOT EXISTS "results" (
	"result_id"	INTEGER,
	"tournament_id"	INTEGER NOT NULL,
	"deck_id"	INTEGER,
	"result"	INTEGER NOT NULL,
	"player_id"	INTEGER,
	PRIMARY KEY("result_id" AUTOINCREMENT),
	FOREIGN KEY("deck_id") REFERENCES "decks"("deck_id"),
	FOREIGN KEY("player_id") REFERENCES "players"("player_id"),
	FOREIGN KEY("tournament_id") REFERENCES "tournaments"("tournament_id")
);
CREATE TABLE IF NOT EXISTS "tournaments" (
	"tournament_id"	INTEGER,
	"date"	TEXT,
	"level"	TEXT,
	"location"	TEXT,
	"name"	TEXT,
	"link"	TEXT,
	PRIMARY KEY("tournament_id" AUTOINCREMENT)
);
INSERT INTO "bases" VALUES (4,'Tarkintown',1,'aggression','rare','TT');
INSERT INTO "bases" VALUES (5,'Energy Conversion Lab',1,'command','rare','ECL');
INSERT INTO "bases" VALUES (7,'Pau City',3,'vigilance','rare',NULL);
INSERT INTO "bases" VALUES (8,'Security Complex',1,'vigilance','rare',NULL);
INSERT INTO "bases" VALUES (9,'Petranaki Arena',3,'cunning','rare',NULL);
INSERT INTO "bases" VALUES (10,'Droid Manufactory',3,'command','rare',NULL);
INSERT INTO "bases" VALUES (11,'Sundari',3,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (12,'Administrator''s Tower',1,'cunning','common',NULL);
INSERT INTO "bases" VALUES (13,'The Nest',3,'aggression','common',NULL);
INSERT INTO "bases" VALUES (14,'Chopper Base',1,'cunning','common',NULL);
INSERT INTO "bases" VALUES (15,'Echo Base',1,'command','common',NULL);
INSERT INTO "bases" VALUES (16,'Pyke Palace',3,'cunning','common',NULL);
INSERT INTO "bases" VALUES (17,'Mos Eisley',4,'cunning','common',NULL);
INSERT INTO "bases" VALUES (18,'Level 1313',3,'cunning','common',NULL);
INSERT INTO "bases" VALUES (19,'Dagobah Swamp',1,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (20,'The Crystal City',3,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (21,'Data Vault',4,'command','rare','DV');
INSERT INTO "bases" VALUES (22,'Thermal Oscillator',4,'aggression','rare',NULL);
INSERT INTO "bases" VALUES (23,'Colossus',4,'vigilance','rare',NULL);
INSERT INTO "bases" VALUES (24,'Nadiri Dockyards',4,'aggression','common',NULL);
INSERT INTO "bases" VALUES (25,'Theed Palace',4,'command','common',NULL);
INSERT INTO "bases" VALUES (26,'Resistance Headquarters',4,'command','common',NULL);
INSERT INTO "bases" VALUES (27,'Jabba''s Palace',2,'cunning','common',NULL);
INSERT INTO "bases" VALUES (28,'Capital City',1,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (29,'Coronet City',2,'cunning','common',NULL);
INSERT INTO "bases" VALUES (30,'Maz Kanata''s Castle',2,'command','common',NULL);
INSERT INTO "bases" VALUES (31,'Lake Country',4,NULL,'rare',NULL);
INSERT INTO "bases" VALUES (32,'Catacombs of Cadera',1,'aggression','common',NULL);
INSERT INTO "bases" VALUES (33,'Command Center',1,'command','common',NULL);
INSERT INTO "bases" VALUES (34,'Shield Generator Complex',4,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (35,'Remote Village',2,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (36,'City in the Clouds',1,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (37,'Nabat Village',4,'cunning','rare',NULL);
INSERT INTO "bases" VALUES (38,'Tipoca City',3,'command','common',NULL);
INSERT INTO "bases" VALUES (39,'Nevarro City',2,'command','common',NULL);
INSERT INTO "bases" VALUES (40,'Remnant Science Facility',2,'vigilance','common',NULL);
INSERT INTO "bases" VALUES (41,'Kestro City',1,'aggression','common',NULL);
INSERT INTO "bases" VALUES (42,'Massassi Temple',4,'aggression','common',NULL);
INSERT INTO "bases" VALUES (43,'Jedha City',1,'cunning','rare',NULL);
INSERT INTO "bases" VALUES (44,'Death Watch Hideout',2,'aggression','common',NULL);
INSERT INTO "bases" VALUES (45,'Lair of Grievous',3,'command','common',NULL);
INSERT INTO "bases" VALUES (110,'Spice Mines',2,'aggression','common',NULL);
INSERT INTO "bases" VALUES (127,'KCM Mining Facility',3,'aggression','common',NULL);
INSERT INTO "bases" VALUES (362,'Shadow Collective Camp',3,'aggression','rare',NULL);
INSERT INTO "cards" VALUES (1,'First Order Stormtrooper',NULL,'unit');
INSERT INTO "cards" VALUES (2,'Greedo','Slow on the Draw','unit');
INSERT INTO "cards" VALUES (3,'ISB Agent',NULL,'unit');
INSERT INTO "cards" VALUES (4,'War Juggernaut',NULL,'unit');
INSERT INTO "cards" VALUES (5,'Guerilla Soldier',NULL,'unit');
INSERT INTO "cards" VALUES (6,'Crafty Smuggler',NULL,'unit');
INSERT INTO "cards" VALUES (7,'Devastator','Hunting the Rebellion','unit');
INSERT INTO "cards" VALUES (8,'Elite P-38 Starfighter',NULL,'unit');
INSERT INTO "cards" VALUES (9,'Ruthless Raider',NULL,'unit');
INSERT INTO "cards" VALUES (10,'Zygerrian Starhopper',NULL,'unit');
INSERT INTO "cards" VALUES (11,'Geonosis Patrol Fighter',NULL,'unit');
INSERT INTO "cards" VALUES (12,'Seventh Fleet Defender',NULL,'unit');
INSERT INTO "cards" VALUES (13,'IG-2000','Assassin''s Aggressor','unit');
INSERT INTO "cards" VALUES (14,'Guavian Antagonizer',NULL,'unit');
INSERT INTO "cards" VALUES (15,'Sneak Attack',NULL,'event');
INSERT INTO "cards" VALUES (16,'Surprise Strike',NULL,'event');
INSERT INTO "cards" VALUES (17,'Triple Dark Raid',NULL,'event');
INSERT INTO "cards" VALUES (18,'Daring Raid',NULL,'event');
INSERT INTO "cards" VALUES (19,'No Good to Me Dead',NULL,'event');
INSERT INTO "cards" VALUES (20,'Armed to the Teeth',NULL,'upgrade');
INSERT INTO "cards" VALUES (21,'Cham Syndulla','Rallying Ryloth','unit');
INSERT INTO "cards" VALUES (22,'Allegiant General Pryde','Ruthless and Loyal','unit');
INSERT INTO "cards" VALUES (23,'Lurking TIE Phantom',NULL,'unit');
INSERT INTO "cards" VALUES (24,'Radiant VII','Ambassadors'' Arrival','unit');
INSERT INTO "cards" VALUES (25,'Kylo''s TIE Silencer','Ruthlessly Efficient','unit');
INSERT INTO "cards" VALUES (26,'Droid Missile Platform',NULL,'unit');
INSERT INTO "cards" VALUES (27,'Fett''s Firespray','Pursuing the Bounty','unit');
INSERT INTO "cards" VALUES (28,'Swoop Down',NULL,'event');
INSERT INTO "cards" VALUES (29,'Waylay',NULL,'event');
INSERT INTO "cards" VALUES (30,'Commandeer',NULL,'event');
INSERT INTO "cards" VALUES (31,'Disabling Fang Fighter',NULL,'unit');
INSERT INTO "cards" VALUES (32,'Force Choke',NULL,'event');
INSERT INTO "cards" VALUES (33,'Lux Bonteri','Renegade Separatist','unit');
INSERT INTO "cards" VALUES (34,'Planetary Bombardment',NULL,'event');
INSERT INTO "cards" VALUES (35,'Plo Koon','Koh-to-yah!','unit');
INSERT INTO "cards" VALUES (36,'Qi''ra','Playing Her Part','unit');
INSERT INTO "cards" VALUES (37,'R2-D2','Ignoring Protocol','unit');
INSERT INTO "cards" VALUES (38,'Sabine Wren','Explosives Artist','unit');
INSERT INTO "cards" VALUES (39,'Soldier of the 501st',NULL,'unit');
INSERT INTO "cards" VALUES (40,'X-34 Landspeeder',NULL,'unit');
INSERT INTO "cards" VALUES (41,'Ahsoka Tano','Chasing Whispers','unit');
INSERT INTO "cards" VALUES (42,'Cassian Andor','Rebellions Are Built On Hope','unit');
INSERT INTO "cards" VALUES (43,'Ezra Bridger','Resourceful Troublemaker','unit');
INSERT INTO "cards" VALUES (44,'Grogu','Irresistible','unit');
INSERT INTO "cards" VALUES (45,'Cartel Turncoat',NULL,'unit');
INSERT INTO "cards" VALUES (46,'Millennium Falcon','Piece of Junk','unit');
INSERT INTO "cards" VALUES (47,'Millennium Falcon','Lando''s Pride','unit');
INSERT INTO "cards" VALUES (48,'Red Five','Running the Trench','unit');
INSERT INTO "cards" VALUES (49,'Sabine''s Masterpiece','Crazy Colorful','unit');
INSERT INTO "cards" VALUES (50,'Force Throw',NULL,'event');
INSERT INTO "cards" VALUES (51,'Jam Communications',NULL,'event');
INSERT INTO "cards" VALUES (52,'Hotshot DL-44 Blaster',NULL,'upgrade');
INSERT INTO "cards" VALUES (53,'Han Solo','Reluctant Hero','unit');
INSERT INTO "cards" VALUES (54,'Sidon Ithano','The Crimson Corsair','unit');
INSERT INTO "cards" VALUES (55,'Krayt Dragon',NULL,'unit');
INSERT INTO "cards" VALUES (56,'L3-37','Droid Revolutionary','unit');
INSERT INTO "cards" VALUES (57,'Red Squadron Y-Wing',NULL,'unit');
INSERT INTO "cards" VALUES (58,'Spark of Rebellion',NULL,'event');
INSERT INTO "cards" VALUES (59,'Bamboozle',NULL,'event');
INSERT INTO "cards" VALUES (60,'Pillage',NULL,'event');
INSERT INTO "cards" VALUES (61,'Change of Heart',NULL,'event');
INSERT INTO "cards" VALUES (62,'Anakin Skywalker','I''ll Try Spinning','unit');
INSERT INTO "cards" VALUES (63,'Poe Dameron','Quick to Improvise','unit');
INSERT INTO "cards" VALUES (64,'Enfys Nest','Champion of Justice','unit');
INSERT INTO "cards" VALUES (65,'Green Squadron A-Wing',NULL,'unit');
INSERT INTO "cards" VALUES (66,'Electromagnetic Pulse',NULL,'event');
INSERT INTO "cards" VALUES (67,'K-2SO','Cassian''s Counterpart','unit');
INSERT INTO "cards" VALUES (68,'Spare the Target',NULL,'event');
INSERT INTO "cards" VALUES (69,'Han Solo','Has His Moments','unit');
INSERT INTO "cards" VALUES (70,'Fireball','An Explosion With Wings','unit');
INSERT INTO "cards" VALUES (71,'Bombing Run',NULL,'event');
INSERT INTO "cards" VALUES (72,'Boba Fett','Disintegrator','unit');
INSERT INTO "cards" VALUES (73,'Death Star Stormtrooper',NULL,'unit');
INSERT INTO "cards" VALUES (74,'Shuttle ST-149','Under Krennic''s Authority','unit');
INSERT INTO "cards" VALUES (75,'Cad Bane','Hostage Taker','unit');
INSERT INTO "cards" VALUES (76,'Emperor Palpatine','Master of the Dark Side','unit');
INSERT INTO "cards" VALUES (77,'Supreme Leader Snoke','Shadow Ruler','unit');
INSERT INTO "cards" VALUES (78,'The Client','Dictated by Discretion','unit');
INSERT INTO "cards" VALUES (79,'Avenger','Hunting Star Destroyer','unit');
INSERT INTO "cards" VALUES (80,'Grenade Strike',NULL,'event');
INSERT INTO "cards" VALUES (81,'Make an Opening',NULL,'event');
INSERT INTO "cards" VALUES (82,'No Glory, Only Results',NULL,'event');
INSERT INTO "cards" VALUES (83,'Open Fire',NULL,'event');
INSERT INTO "cards" VALUES (84,'Power of the Dark Side',NULL,'event');
INSERT INTO "cards" VALUES (85,'Shoot Down',NULL,'event');
INSERT INTO "cards" VALUES (86,'Superlaser Blast',NULL,'event');
INSERT INTO "cards" VALUES (87,'Takedown',NULL,'event');
INSERT INTO "cards" VALUES (88,'Vigilance',NULL,'event');
INSERT INTO "cards" VALUES (89,'Merciless Contest',NULL,'event');
INSERT INTO "cards" VALUES (90,'Restock',NULL,'event');
INSERT INTO "cards" VALUES (91,'Rival''s Fall',NULL,'event');
INSERT INTO "cards" VALUES (92,'Death Mark',NULL,'upgrade');
INSERT INTO "cards" VALUES (93,'Perilous Position',NULL,'upgrade');
INSERT INTO "cards" VALUES (94,'Top Target',NULL,'upgrade');
INSERT INTO "cards" VALUES (95,'Bazine Netal','Spy for the First Order','unit');
INSERT INTO "cards" VALUES (96,'Mission Briefing',NULL,'event');
INSERT INTO "cards" VALUES (97,'Lieutenant Childsen','Death Star Prison Warden','unit');
INSERT INTO "cards" VALUES (98,'Bounty Hunter Crew',NULL,'unit');
INSERT INTO "cards" VALUES (99,'Bodhi Rook','Imperial Defector','unit');
INSERT INTO "cards" VALUES (100,'DJ','Blatant Thief','unit');
INSERT INTO "cards" VALUES (101,'Liberated Slaves',NULL,'unit');
INSERT INTO "cards" VALUES (102,'Tech','Source of Insight','unit');
INSERT INTO "cards" VALUES (103,'Cantina Bouncer',NULL,'unit');
INSERT INTO "cards" VALUES (104,'The Mandalorian','Weathered Pilot','unit');
INSERT INTO "cards" VALUES (105,'Zorii Bliss','Valiant Smuggler','unit');
INSERT INTO "cards" VALUES (106,'Tantive IV','Fleeing the Empire','unit');
INSERT INTO "cards" VALUES (107,'Cunning',NULL,'event');
INSERT INTO "cards" VALUES (108,'Criminal Muscle',NULL,'unit');
INSERT INTO "cards" VALUES (109,'Infiltrating Demolisher',NULL,'unit');
INSERT INTO "cards" VALUES (110,'Reckless Gunslinger',NULL,'unit');
INSERT INTO "cards" VALUES (111,'Heavy Persuader Tank',NULL,'unit');
INSERT INTO "cards" VALUES (112,'On the Doorstep',NULL,'event');
INSERT INTO "cards" VALUES (113,'Clear the Field',NULL,'event');
INSERT INTO "cards" VALUES (114,'Political Pressure',NULL,'event');
INSERT INTO "cards" VALUES (115,'Stay on Target',NULL,'event');
INSERT INTO "cards" VALUES (116,'Stolen AT-Hauler',NULL,'unit');
INSERT INTO "cards" VALUES (117,'A New Adventure',NULL,'event');
INSERT INTO "cards" VALUES (118,'Cartel Spacer',NULL,'unit');
INSERT INTO "cards" VALUES (119,'4-LOM','Bounty Hunter for Hire','unit');
INSERT INTO "cards" VALUES (120,'Bossk','Deadly Stalker','unit');
INSERT INTO "cards" VALUES (121,'Boba Fett','Feared Bounty Hunter','unit');
INSERT INTO "cards" VALUES (122,'Zuckuss','Bounty Hunter for Hire','unit');
INSERT INTO "cards" VALUES (123,'Contracted Jumpmaster',NULL,'unit');
INSERT INTO "cards" VALUES (124,'Mist Hunter','The Findsman''s Pursuit','unit');
INSERT INTO "cards" VALUES (125,'Ma Klounkee',NULL,'event');
INSERT INTO "cards" VALUES (126,'Relentless Pursuit',NULL,'event');
INSERT INTO "cards" VALUES (127,'Jabba the Hutt','Cunning Daimyo','unit');
INSERT INTO "cards" VALUES (128,'Mace Windu','Party Crasher','unit');
INSERT INTO "cards" VALUES (129,'Mercenary Gunship',NULL,'unit');
INSERT INTO "cards" VALUES (130,'Sanctioner''s Shuttle',NULL,'unit');
INSERT INTO "cards" VALUES (131,'Torpedo Barrage',NULL,'event');
INSERT INTO "cards" VALUES (132,'Alliance Dispatcher',NULL,'unit');
INSERT INTO "cards" VALUES (133,'Battlefield Marine',NULL,'unit');
INSERT INTO "cards" VALUES (134,'Kanan Jarrus','Revealed Jedi','unit');
INSERT INTO "cards" VALUES (135,'Luke Skywalker','Jedi Knight','unit');
INSERT INTO "cards" VALUES (136,'Village Protectors',NULL,'unit');
INSERT INTO "cards" VALUES (137,'Admiral Yularen','Fleet Coordinator','unit');
INSERT INTO "cards" VALUES (138,'Chewbacca','Faithful First Mate','unit');
INSERT INTO "cards" VALUES (139,'Hera Syndulla','We''ve Lost Enough','unit');
INSERT INTO "cards" VALUES (140,'Obi-Wan Kenobi','Following Fate','unit');
INSERT INTO "cards" VALUES (141,'Yoda','Old Master','unit');
INSERT INTO "cards" VALUES (142,'Concord Dawn Interceptors',NULL,'unit');
INSERT INTO "cards" VALUES (143,'Restored ARC-170',NULL,'unit');
INSERT INTO "cards" VALUES (144,'Blue Leader','Scarif Air Support','unit');
INSERT INTO "cards" VALUES (145,'Bright Hope','The Last Transport','unit');
INSERT INTO "cards" VALUES (146,'Home One','Alliance Flagship','unit');
INSERT INTO "cards" VALUES (147,'Phoenix Squadron A-Wing',NULL,'unit');
INSERT INTO "cards" VALUES (148,'Redemption','Medical Frigate','unit');
INSERT INTO "cards" VALUES (149,'Fell the Dragon',NULL,'event');
INSERT INTO "cards" VALUES (150,'Resupply',NULL,'event');
INSERT INTO "cards" VALUES (151,'U-Wing Reinforcement',NULL,'event');
INSERT INTO "cards" VALUES (152,'Luke''s Lightsaber',NULL,'upgrade');
INSERT INTO "cards" VALUES (153,'Scanning Officer',NULL,'unit');
INSERT INTO "cards" VALUES (154,'Echo Base Defender',NULL,'unit');
INSERT INTO "cards" VALUES (155,'Confiscate',NULL,'event');
INSERT INTO "cards" VALUES (156,'Traitorous',NULL,'upgrade');
INSERT INTO "cards" VALUES (157,'Jetpack',NULL,'upgrade');
INSERT INTO "cards" VALUES (158,'Gamorrean Guards',NULL,'unit');
INSERT INTO "cards" VALUES (159,'Confederate Tri-Fighter',NULL,'unit');
INSERT INTO "cards" VALUES (160,'Now There Are Two of Them',NULL,'event');
INSERT INTO "cards" VALUES (161,'Darth Vader','Scourge of Squadrons','unit');
INSERT INTO "cards" VALUES (162,'B1 Security Team',NULL,'unit');
INSERT INTO "cards" VALUES (163,'Bib Fortuna','Jabba''s Majordomo','unit');
INSERT INTO "cards" VALUES (164,'Separatist Commando',NULL,'unit');
INSERT INTO "cards" VALUES (165,'Superlaser Technician',NULL,'unit');
INSERT INTO "cards" VALUES (166,'Droid Commando',NULL,'unit');
INSERT INTO "cards" VALUES (167,'Maul','Shadow Collective Visionary','unit');
INSERT INTO "cards" VALUES (168,'Reinforcement Walker',NULL,'unit');
INSERT INTO "cards" VALUES (169,'Devastator','Inescapable','unit');
INSERT INTO "cards" VALUES (170,'Resupply Carrier',NULL,'unit');
INSERT INTO "cards" VALUES (171,'The Invisible Hand','Crawling With Vultures','unit');
INSERT INTO "cards" VALUES (172,'Arquitens Assault Cruiser',NULL,'unit');
INSERT INTO "cards" VALUES (173,'Chimaera','Flagship of the Seventh Fleet','unit');
INSERT INTO "cards" VALUES (174,'Finalizer','Might of the First Order','unit');
INSERT INTO "cards" VALUES (175,'Invincible','Naval Adversary','unit');
INSERT INTO "cards" VALUES (176,'Overwhelming Barrage',NULL,'event');
INSERT INTO "cards" VALUES (177,'Dogfight',NULL,'event');
INSERT INTO "cards" VALUES (178,'Jump to Lightspeed',NULL,'event');
INSERT INTO "cards" VALUES (179,'Outlaw Corona',NULL,'unit');
INSERT INTO "cards" VALUES (180,'Relentless','Konstantine''s Folly','unit');
INSERT INTO "cards" VALUES (181,'System Shock',NULL,'event');
INSERT INTO "cards" VALUES (182,'Poggle the Lesser','Archduke of the Stalgasin Hive','unit');
INSERT INTO "cards" VALUES (183,'Salacious Crumb','Obnoxious Pet','unit');
INSERT INTO "cards" VALUES (184,'Syndicate Lackeys',NULL,'unit');
INSERT INTO "cards" VALUES (185,'Colonel Yularen','ISB Director','unit');
INSERT INTO "cards" VALUES (186,'Darth Vader','Commanding the First Legion','unit');
INSERT INTO "cards" VALUES (187,'Frozen in Carbonite',NULL,'upgrade');
INSERT INTO "cards" VALUES (188,'Palpatine''s Return',NULL,'event');
INSERT INTO "cards" VALUES (189,'Phase-III Dark Trooper',NULL,'unit');
INSERT INTO "cards" VALUES (190,'Cobb Vanth','The Marshal','unit');
INSERT INTO "cards" VALUES (191,'Director Krennic','On the Verge of Greatness','unit');
INSERT INTO "cards" VALUES (192,'Emperor''s Royal Guard',NULL,'unit');
INSERT INTO "cards" VALUES (193,'Pantoran Starship Thief',NULL,'unit');
INSERT INTO "cards" VALUES (194,'Confederate Courier',NULL,'unit');
INSERT INTO "cards" VALUES (195,'Entrenched',NULL,'upgrade');
INSERT INTO "cards" VALUES (196,'Luke Skywalker','You Still With Me?','unit');
INSERT INTO "cards" VALUES (197,'Millennium Falcon','Get Out And Push','unit');
INSERT INTO "cards" VALUES (198,'The Marauder','Shuttling the Bad Batch','unit');
INSERT INTO "cards" VALUES (199,'Salvage',NULL,'event');
INSERT INTO "cards" VALUES (200,'Boba Fett''s Armor',NULL,'upgrade');
INSERT INTO "cards" VALUES (201,'Fleet Lieutenant',NULL,'unit');
INSERT INTO "cards" VALUES (202,'Sundari Peacekeeper',NULL,'unit');
INSERT INTO "cards" VALUES (203,'Wrecker','Boom!','unit');
INSERT INTO "cards" VALUES (204,'For a Cause I Believe In',NULL,'event');
INSERT INTO "cards" VALUES (205,'Rebel Assault',NULL,'event');
INSERT INTO "cards" VALUES (206,'Timely Intervention',NULL,'event');
INSERT INTO "cards" VALUES (207,'The Darksaber',NULL,'upgrade');
INSERT INTO "cards" VALUES (208,'General Dodonna','Massassi Group Commander','unit');
INSERT INTO "cards" VALUES (209,'Kuiil','I Have Spoken','unit');
INSERT INTO "cards" VALUES (210,'Regional Governor',NULL,'unit');
INSERT INTO "cards" VALUES (211,'Covering the Wing',NULL,'event');
INSERT INTO "cards" VALUES (212,'Bravado',NULL,'event');
INSERT INTO "cards" VALUES (213,'Jedi Lightsaber',NULL,'upgrade');
INSERT INTO "cards" VALUES (214,'Steela Gerrera','Beloved Tactician','unit');
INSERT INTO "cards" VALUES (215,'Huyang','Enduring Instructor','unit');
INSERT INTO "cards" VALUES (216,'Admiral Yularen','Advising Caution','unit');
INSERT INTO "cards" VALUES (217,'General Rieekan','Defensive Strategist','unit');
INSERT INTO "cards" VALUES (218,'Obi-Wan''s Aethersprite','This is Why I Hate Flying','unit');
INSERT INTO "cards" VALUES (219,'Direct Hit',NULL,'event');
INSERT INTO "cards" VALUES (220,'Spark of Hope',NULL,'event');
INSERT INTO "cards" VALUES (221,'The Force Is With Me',NULL,'event');
INSERT INTO "cards" VALUES (222,'General''s Blade',NULL,'upgrade');
INSERT INTO "leaders" VALUES (1,'Han Solo','Worth the Risk',2,'han2','aggression','heroism');
INSERT INTO "leaders" VALUES (2,'Yoda','Sensing Darkness',3,'yoda','vigilance','heroism');
INSERT INTO "leaders" VALUES (3,'Sabine Wren','Galvanized Revolutionary',1,'sabine','aggression','heroism');
INSERT INTO "leaders" VALUES (4,'Quinlan Vos','Sticking the Landing',3,'quinlan','cunning','heroism');
INSERT INTO "leaders" VALUES (5,'Cad Bane','He Who Needs No Introduction',2,'cad bane','cunning','villainy');
INSERT INTO "leaders" VALUES (6,'Emperor Palpatine','Galactic Ruler',1,'palp1','command','villainy');
INSERT INTO "leaders" VALUES (7,'Chancellor Palpatine','Playing Both Sides',3,'palp3','cunning','heroism');
INSERT INTO "leaders" VALUES (8,'Jango Fett','Concealing the Conspiracy',3,'jango','cunning','villainy');
INSERT INTO "leaders" VALUES (9,'Han Solo','Audacious Smuggler',1,'han1','cunning','heroism');
INSERT INTO "leaders" VALUES (10,'Bossk','Hunting His Prey',2,'bossk','aggression','villainy');
INSERT INTO "leaders" VALUES (11,'Rey','More Than a Scavenger',2,'rey','vigilance','heroism');
INSERT INTO "leaders" VALUES (12,'Obi-Wan Kenobi','Patient Mentor',3,'obi-wan','vigilance','heroism');
INSERT INTO "leaders" VALUES (13,'Iden Versio','Inferno Squad Commander',1,'iden','vigilance','villainy');
INSERT INTO "leaders" VALUES (14,'Luke Skywalker','Faithful Friend',1,'luke','vigilance','heroism');
INSERT INTO "leaders" VALUES (15,'Maul','A Rival in Darkness',3,'maul','aggression','villainy');
INSERT INTO "leaders" VALUES (16,'Director Krennic','Aspiring to Authority',1,'krennic','vigilance','villainy');
INSERT INTO "leaders" VALUES (17,'Qi''ra','I Alone Survived',2,'qira','vigilance','villainy');
INSERT INTO "leaders" VALUES (18,'Grand Moff Tarkin','Oversector Governor',1,'tarkin','command','villainy');
INSERT INTO "leaders" VALUES (19,'Anakin Skywalker','What it Takes to Win',3,'anakin','aggression','heroism');
INSERT INTO "leaders" VALUES (20,'Fennec Shand','Honoring the Deal',2,'fennec','cunning','heroism');
INSERT INTO "leaders" VALUES (21,'Asajj Ventress','Unparalleled Adversary',3,'asajj3','cunning','villainy');
INSERT INTO "leaders" VALUES (22,'Cassian Andor','Dedicated to the Rebellion',1,'cassian','aggression','heroism');
INSERT INTO "leaders" VALUES (23,'Hondo Ohnaka','That''s Good Business',2,'hondo','command','villainy');
INSERT INTO "leaders" VALUES (24,'Darth Vader','Dark Lord of the Sith',1,'vader','aggression','villainy');
INSERT INTO "leaders" VALUES (25,'Jabba the Hutt','His High Exaltedness',2,'jabba','command','villainy');
INSERT INTO "leaders" VALUES (27,'Kylo Ren','Rash and Deadly',2,'kylo','aggression','villainy');
INSERT INTO "leaders" VALUES (28,'Mace Windu','Vaapad Form Master',3,'mace','aggression','heroism');
INSERT INTO "leaders" VALUES (29,'Moff Gideon','Formidable Commander',2,'gideon','command','villainy');
INSERT INTO "leaders" VALUES (30,'Grand Admiral Thrawn','Patient and Insightful',1,'thrawn1','cunning','villainy');
INSERT INTO "leaders" VALUES (31,'Count Dooku','Face of the Confederacy',3,'dooku','command','villainy');
INSERT INTO "leaders" VALUES (32,'Pre Vizsla','Pursuing the Throne',3,'pre vizsla','aggression','villainy');
INSERT INTO "leaders" VALUES (33,'Boba Fett','Daimyo',2,'boba2','command','heroism');
INSERT INTO "leaders" VALUES (34,'Gar Saxon','Viceroy of Mandalore',2,'gar saxon','vigilance','villainy');
INSERT INTO "leaders" VALUES (35,'Wat Tambor','Techno Union Foreman',3,'wat tambor','command','villainy');
INSERT INTO "leaders" VALUES (36,'Bo-Katan Kryze','Princess in Exile',2,'bo-katan','aggression','heroism');
INSERT INTO "leaders" VALUES (37,'IG-88','Ruthless Bounty Hunter',1,'ig-88','aggression','villainy');
INSERT INTO "leaders" VALUES (38,'Admiral Piett','Commanding the Armada',4,'piett','command','villainy');
INSERT INTO "leaders" VALUES (39,'Kazuda Xiono','Best Pilot in the Galaxy',4,'kazuda','cunning','heroism');
INSERT INTO "leaders" VALUES (40,'Poe Dameron','I Can Fly Anything',4,'poe','aggression','heroism');
INSERT INTO "leaders" VALUES (41,'Darth Vader','Victor Squadron Leader',4,'vader4','command','villainy');
INSERT INTO "leaders" VALUES (42,'Grand Admiral Thrawn','...How Unfortunate',4,'thrawn4','vigilance','villainy');
INSERT INTO "leaders" VALUES (43,'Captain Rex','Fighting For His Brothers',3,'rex','command','heroism');
INSERT INTO "leaders" VALUES (44,'Admiral Trench','Chk-chk-chk-chk',4,'trench','cunning','villainy');
INSERT INTO "leaders" VALUES (45,'Luke Skywalker','Hero of Yavin',4,'luke4','aggression','heroism');
INSERT INTO "leaders" VALUES (46,'Boba Fett','Any Methods Necessary',4,'boba4','aggression','villainy');
INSERT INTO "leaders" VALUES (47,'Captain Phasma','Chrome Dome',4,'phasma','aggression','villainy');
INSERT INTO "leaders" VALUES (48,'Han Solo','Never Tell Me the Odds',4,'han4','cunning','heroism');
INSERT INTO "leaders" VALUES (49,'Leia Organa','Alliance General',1,'leia','command','heroism');
INSERT INTO "leaders" VALUES (50,'The Mandalorian','Sworn To The Creed',2,'mando','cunning','heroism');
INSERT INTO "leaders" VALUES (51,'Hera Syndulla','Spectre Two',1,'hera','command','heroism');
INSERT INTO "leaders" VALUES (52,'Wedge Antilles','Leader of Red Squadron',4,'wedge','command','heroism');
INSERT INTO "leaders" VALUES (53,'Asajj Ventress','I Work Alone',4,'asajj4','vigilance','villainy');
INSERT INTO "leaders" VALUES (54,'Rio Durant','Wisecracking Wheelman',4,'rio_durant','cunning','villainy');
INSERT INTO "leaders" VALUES (55,'Grand Inquisitor','Hunting the Jedi',1,'grand_inquisitor','aggression','villainy');
INSERT INTO "leaders" VALUES (8398,'Major Vonreg','Red Baron',4,'vonreg','aggression','villainy');
INSERT INTO "leaders" VALUES (8399,'Lando Calrissian','Buying Time',4,'lando4','vigilance','heroism');
INSERT INTO "leaders" VALUES (8400,'Ahsoka Tano','Snips',3,'ahsoka','aggression','heroism');
INSERT INTO "leaders" VALUES (8401,'Doctor Aphra','Rapacious Archaeologist',2,'aphra','cunning','villainy');
INSERT INTO "leaders" VALUES (8402,'Admiral Ackbar','It''s A Trap!',4,'ackbar','cunning','heroism');
INSERT INTO "leaders" VALUES (8403,'Rose Tico','Saving What We Love',4,'rose','vigilance','heroism');
INSERT INTO "leaders" VALUES (8404,'General Grievous','General of the Droid Armies',3,'grievous','cunning','villainy');
INSERT INTO "leaders" VALUES (8405,'Nala Se','Clone Engineer',3,'nala_se','vigilance','villainy');
INSERT INTO "leaders" VALUES (8410,'Chirrut Îmwe','One With The Force',1,'chirrut','vigilance','heroism');
INSERT INTO "leaders" VALUES (8411,'Padmé Amidala','Serving the Republic',3,'padme','command','heroism');
INSERT INTO "leaders" VALUES (8412,'Admiral Holdo','We''re Not Alone',4,'holdo','command','heroism');
INSERT INTO "leaders" VALUES (8413,'Lando Calrissian','With Impeccable Taste',2,'lando2','cunning','heroism');
INSERT INTO "leaders" VALUES (8414,'Hunter','Outcast Sergeant',2,'hunter','command','heroism');
INSERT INTO "leaders" VALUES (8415,'Jyn Erso','Resisting Oppression',1,'jyn_erso','cunning','heroism');
INSERT INTO "leaders" VALUES (8416,'Chewbacca','Walking Carpet',1,'chewie','vigilance','heroism');
CREATE INDEX IF NOT EXISTS "idx_results_player_id" ON "results" (
	"player_id"
);
COMMIT;
