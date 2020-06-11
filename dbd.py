#
##
### DEAD BY DAYLIGHT STUFF AND THING UTILITY
##
#
# ???
# TODO: use log files to track match history with maps+players as well?
# TODO: save last modified date of log + line length?
# TODO: attempt to determine whether or not survivor is in an active lobby
# TODO: SWITCH TO REGEX...?
# TODO: dbd crash -> boinked linenum
# TODO: desynced linenums warning?
# TODO: exit gates, timer to first exit gate light, unhook cancels



#TODO: killer locker x4, empty locker 0 seconds x2
# toolbox repair
# mending
# hexes
# items from chests/track items?
# endurance
# killer leaving lobby doesn't work
# ds timer notification?
# genid for kicked gens

import time, os, urllib.request
#import requests

dbdKillers = {'56':'Trapper',
              '57':'Wraith',
              '58':'Hillbilly',
              '59':'Nurse',
              '60':'Hag',
              '61':'Michael Myers',
              '62':'Doctor',
              '63':'Huntress',
              '64':'Leatherface',
              '65':'Freddy Krueger',
              '66':'Pig',
              '67':'Clown',
              '68':'Spirit',
              '69':'Legion',
              '70':'Plague',
              '71':'Ghostface',
              '72':'Demogorgon',
              '73':'Oni',
              '74':'Deathslinger',
              '75':'Pyramid Head'}

dbdMaps = {'CoalTower':'MacMillan Estate: Coal Tower',                  # Ind_
           'Storehouse':'MacMillan Estate: Groaning Storehouse',
           'Foundry':'MacMillan Estate: Ironworks of Misery',
           'Forest':'MacMillan Estate: Shelter Woods',
           'Mine':'MacMillan Estate: Suffocation Pit',
           'Office':'Autohaven Wreckers: Azarov\'s Resting Place',      # Jnk_
           'Lodge':'Autohaven Wreckers: Blood Lodge',
           'GasStation':'Autohaven Wreckers: Gas Heaven',
           'Scrapyard':'Autohaven Wreckers: Wreckers\'s Yard',
           'Garage':'Autohaven Wreckers: Wretched Shop',
           'Barn':'Coldwind Farm: Fractured Cowshed',                   # Frm_
           'Slaughterhouse':'Coldwind Farm: Rancid Abattoir',
           'Cornfield':'Coldwind Farm: Rotten Fields',
           'Farmhouse':'Coldwind Farm: The Thompson House',
           'Silo':'Coldwind Farm: Torment Creek',
           'Asylum':'Crotus Prenn Asylum: Disturbed Ward',
           'Chapel':'Crotus Prenn Asylum: Father Campbell\'s Chapel',
           'Street':'Haddonfield: Lampkin Lane',
           'PaleRose':'Backwater Swamp: The Pale Rose',
           'GrimPantry':'Backwater Swamp: Grim Pantry',
           'Treatment':'Léry\'s Memorial Institute: Treatment Theatre',
           'MaHouse':'Red Forest: Mother\'s Dwelling',
           'Temple':'Red Forest: Temple of Purgation',
           'Street_01':'Springwood: Badham Preschool I',
           'Street_02':'Springwood: Badham Preschool II',
           'Street_03':'Springwood: Badham Preschool III',
           'Street_04':'Springwood: Badham Preschool IV',
           'Street_05':'Springwood: Badham Preschool V',
           'Hideout':'Gideon Meat Plant: The Game',
           'Manor':'Yamaoka Estate: Family Residence',
           'Shrine':'Yamaoka Estate: Sanctum of Wrath',
           'Cottage':'Ormond: Mount Ormond Resort',
           'Lab':'Hawkins National Laboratory: The Underground Complex',    # Qat_
           'Saloon':'Grave of Glenvale: Dead Dawg Saloon'}

dbdLogPath = os.path.expandvars("%LOCALAPPDATA%\\DeadByDaylight\\Saved\\Logs\\DeadByDaylight.log")

#############################################
### --- MATCH ANALYTICS (COMING SOON) --- ###
#############################################
class Match:
    def __init__(self):
        self.matchid = 0
        self.queueStart = 0
        self.queueEnd = 0
        self.queueTime = 0
        self.matchLength = 0

        self.survivors = []
        self.killer = None
        self.map = ''

        self.totemsCleansed = 0
        self.chestsSearched = 0
        self.totemsCleansedTime = 0
        self.chestsSearchedTime = 0

    def __repr__(self):
        pass

class Survivor:
    def __init__(self):
        self.steamid = 0
        self.profileurl = ''
        self.name = ''
        self.totems = 0
        self.chests = 0

class Killer:
    def __init__(self):
        self.steamid = 0
        self.profileurl = ''
        self.name = ''
        self.killer = ''
        self.hooks = 0
#############################################




###########################################
### --- DEAD BY DAYLIGHT LOG READER --- ###
###########################################
class DBDInstance:
    def __init__(self, logPath):
        self.logPath = logPath
        self.logFile = None

        self.gameIsOpen = True
        self.currentTime = time.gmtime()    # unused
        self.lastTime = self.currentTime    # unused
        self.lastPosition = 0
        self.currentPosition = 0

        self.showHistory = True
        self.showKillerNamesInHistory = False
        self.showingHistory = True

        self.isInMenu = False               # unused
        self.isInOfflineLobby = False       # unused
        self.isInOnlineLobby = False        # unused
        self.isInGame = False               # unused

        self.killer = None
        self.lastReadID = None              # unused

        self.matches = []                   # unused
        self.queueStart = 0
        self.queueEnd = 0



    def copyToClipboard(self, text):
        os.system(f'echo {text.strip()}| clip')

    def getTimestamp(self, timestamp):      # TODO: doesn't include ms?
        return time.strftime('%m/%d %I:%M:%S %p',time.strptime(timestamp, '[%Y.%m.%d-%H.%M.%S'))

    def getSteamName(self, profileUrl):
        try:
            #r = requests.get(url=profileUrl, timeout=3)    # TODO: add flag to stop future attempts if one times out
            #return r.text[r.text.find("Steam Community :: ")+19 : r.text.find("</title>")]
            r = str(urllib.request.urlopen(profileUrl).read())
            return r[r.find("Steam Community :: ")+19 : r.find("</title>")]
        except:     # multiple possible timeout exceptions
            print("WARNING: Request for killer's name timed out after 3 seconds.")
            return 0

    def getActionDuration(self, lineNum):
        for i in range(3):
            try:
                duration = self.log[lineNum-(i+1)].split()[-1]
                if duration[-1].isdigit() and '.' in duration:
                    return float(duration)
                break
            except: continue
        return 0



    def parseLog(self):
        for lineNum, logLine in enumerate(self.log):
            line = logLine[30:].strip()
            timestamp = logLine[:20]

            # TODO: is "in" faster than [:]?
            if line[:95] == "LogOnline: Verbose: OSS: Async task 'FOnlineAsyncTaskSteamCreateLobby bWasSuccessful: 1 LobbyId":
                print('Offline lobby created and entered.')


            elif line == "GameFlow: Verbose: [UOnlineSystemHandler::StartQuickmatch]":
                self.queueStart = time.monotonic()
                print('All survivors ready. Searching for online lobby...')


            elif line == "GameFlow: Canceling Matchmaking":
                self.queueStart = 0
                print('Search cancelled.')


            elif line == "LogContextSystem: ContextGroup transition requested: Group: GameFlowContextGroup(0) Context: LoadingContext (ULoadingScreen)(20) Transition: LOADING_TRAVELING_JOINING_LOBBY(6)":
                '''
                LogContextSystem: ContextGroup transition requested: Group: GameFlowContextGroup(0) Context: LoadingContext (ULoadingScreen)(20) Transition: LOADING_TRAVELING_JOINING_LOBBY(6)
                GameFlow: LoadingContextComponent::Enter - TransitionId=LOADING_TRAVELING_JOINING_LOBBY (6)
                GameFlow: LoadingContextComponent::StartLoadingTask - Begin level loading - TransitionId=LOADING_TRAVELING_JOINING_LOBBY (6)
                GameFlow: LoadingContextComponent::RequestTransition - Begin context transition - TransitionId=LOADING_TRAVELING_JOINING_LOBBY (6)
                GameFlow: LoadingContextComponent::Leave - TransitionId=LOADING_TRAVELING_JOINING_LOBBY (6)
                '''
                if not self.showingHistory and self.queueStart:
                    self.queueEnd = time.monotonic()
                    queueTime = round(self.queueEnd - self.queueStart)
                    queueTimestamp = time.strftime(('%H:%M:%S' if queueTime >= 3600 else '%M:%S' if queueTime >= 60 else '%S seconds'), time.gmtime(queueTime))
                    if (600 > queueTime >= 60) or (36000 > queueTime >= 3600):
                        queueTimestamp = queueTimestamp[1:]
                    print(f'\n\nOnline lobby found and entered in {queueTimestamp}.\n{"-"*25}')
                else:
                    print(f'\n\nOnline lobby found and entered.\n{"-"*25}')


            elif line[:100] == "LogOnline: Verbose: Mirrors: [FOnlineSessionMirrors::AddSessionPlayer] Session:GameSession PlayerId:":
                while True:
                    try:
                        cosmeticLine = self.log[lineNum+6]
                        break
                    except IndexError:
                        print('WARNING! IndexError raised while looking for cosmetic lines, re-checking...')
                        self.currentPosition = self.logFile.tell()
                        self.logFile.seek(self.lastPosition)
                        self.log = self.logFile.readlines()
                        self.logFile.seek(self.currentPosition)
                if "_Leg" not in cosmeticLine:
                    killerID = line[137:]
                    killerProfileLink = 'https://steamcommunity.com/profiles/' + killerID
                    self.copyToClipboard(killerProfileLink)
                    print(f"Killer profile: {killerProfileLink}")
                    if not self.showingHistory or self.showKillerNamesInHistory:
                        killerName = self.getSteamName(killerProfileLink)
                        if killerName:
                            print(f"   Killer name: {killerName}")

            elif line[:89] == 'GameFlow: Verbose: [ADBDPlayerState_Menu::ReplacePawn] Spawn new pawn characterId 2684354':
                self.killer = dbdKillers[line[89:91]]
                print(f'Current killer in lobby: {self.killer}')  # TODO add timestamp?



            elif line == "GameFlow: RequestTransition -> LOADING_TRAVELING_TO_GAME":
                print('\nGame starting...')


            elif line[:36] == "ProceduralLevelGeneration: InitLevel":
                mapName = line[line.find('Map:')+9 : line.find(' Generation Seed: -1')]     # isolates map name
                if mapName in dbdMaps:
                    print(f'...loading map "{dbdMaps[mapName]}"')
                else:
                    print(f'...loading unknown map "{mapName}"')


            elif line == "LogContextSystem: ContextGroup transition requested: Group: GameFlowContextGroup(0) Context: LoadingContext (ULoadingScreen)(20) Transition: LOADING_TRAVELING_TO_PARTY_LOBBY(23)":
                '''
                LogContextSystem: ContextGroup transition requested: Group: GameFlowContextGroup(0) Context: LoadingContext (ULoadingScreen)(20) Transition: LOADING_TRAVELING_TO_PARTY_LOBBY(23)
                GameFlow: LoadingContextComponent::Enter - TransitionId=LOADING_TRAVELING_TO_PARTY_LOBBY (23)
                GameFlow: LoadingContextComponent::StartLoadingTask - Begin level loading - TransitionId=LOADING_TRAVELING_TO_PARTY_LOBBY (23)
                GameFlow: LoadingContextComponent::Leave - TransitionId=LOADING_TRAVELING_TO_PARTY_LOBBY (23)
                '''
                print(f'{"-"*25}\n\n\nOnline lobby left, offline lobby re-entered.')


            if not self.showingHistory:
                action = "UNKNOWN_ACTION"

                ##if line[47:] == "SetGuidedAction [VE_BeingPickedUp]":   # TODO: sometimes doesn't go off? might be when you're the one being picked up
                ##    print(f"   Survivor is being picked up ({actionDuration}). 16 seconds until wiggle escape.")    # also remember the 2.7 second delay!!!

                ##if line[40:44] == "Hook" and line.endswith("Duration 1.500000 Timestamp 0.000000"):
                ###Interaction: Interaction time: 1.500000
                ###AnimLeader: BP_Slasher_Character_03_C_0 Requested to Play: HookCamper HillBilly AnimTag_Carry.
                ##    print('   Survivor is being hooked...')

                if line.endswith("<Entering state Hooked>"):
                    print('   ...Killer has HOOKED survivor.')

                ##elif "[RequestAndBeginInteraction] - [Unhook]" in line:
                ###Interaction: Interaction time: 1.000000
                ###AnimLeader: BP_CamperMale01_C_0 Requested to Play: UnhookIn Struggle AnimTag_Male.
                ##    print('   Survivor is being unhooked...')

                ####elif line.endswith("<Exiting state Hooked>") and self.log[lineNum-1].endswith("<Exiting state Unhooking>"):
                ####    print('   ...Survivor has been unhooked.')
                ##elif line[:30] == "Interaction: Verbose: [Unhook]" and line.endswith == "[<!> Charge Complete Received]":
                ##    print('   ...Survivor has been unhooked.')      # TODO: figure out unhook cancel/failure

                #testing
                ##elif line.endswith("<Entering state Draining>"):
                ##    print(' ? Survivor is on their first hook. 60 seconds until struggle.')

                elif line.endswith("<Entering state ReactionIn>"):
                    #<Entering state Struggle> -> timer actually starts
                    print(' ? Survivor has entered the struggle phase...')

                elif line.endswith("<Entering state Struggle>"):
                    print('   ...struggle timer has started. 60 seconds until sacrifice.')

                elif line.endswith("<Entering state Sacrifice>"):   # TODO: check if it logs running out of health vs. giving up on hook
                    print('   Survivor has been SACRIFICED.')       # TODO: moris, dc's

                elif line.endswith("<Entering state CamperEscaped>"):
                    #<Exiting state Playing>
                    #<Entering state CamperDead>
                    print('   Survivor has ESCAPED.')   # TODO: do HatchEscape as well?




                elif line.endswith("is in chase."):
                    print(' ? Survivor is being chased...')
                elif line.endswith("is not in chase anymore."):
                    print(' ? ...Survivor is no longer being chased.')


                elif line[:72] == "LogDBDGeneral: StatusEffect::EndPlay - Id: DecisiveStrike_Notification_2":
                    print(' ? DecisiveStrike_Notification_2')
                elif line[:97] == "LogDBDGeneral: StatusEffect::Multicast_InitializeStatusEffect - Id: DecisiveStrike_Notification_3":
                    print(' ? DecisiveStrike_Notification_3')


                elif line[:38] == "Interaction: Verbose: [GeneratorRepair":
                    #Interaction: Verbose: [GeneratorRepair3][GeneratorStandard_C_1] - [BP_CamperFemale02_Character_C_0 - GoshDammitDog][CLIENT SLAVE] - [<!> Interaction Event OnInteractionUpdateTick]
                    #[RequestAndBeginInteraction] - [GeneratorRepair
                    actionDuration = self.getActionDuration(lineNum)
                    genId = line.split(']')[1][-1]
                    if actionDuration:
                        print(f"   Survivor REPAIRING generator #{genId} ({actionDuration} seconds)...")
                    if line.endswith("[<== Interaction Exit]"):
                        print(f"   ...Survivor stopped REPAIRING generator #{genId}.")
                    elif line.endswith("[<!> Charge Complete Received]"):
                        print(f"      ...Survivor fully REPAIRED generator #{genId}.")
                elif line[:38] == "Interaction: Verbose: [HealOtherMedkit":
                    actionDuration = self.getActionDuration(lineNum)
                    if actionDuration:
                        numSurvivors = int(line[38])     # TODO: include type of medkit?
                        print(f"   {numSurvivors} survivor{'s' if numSurvivors > 1 else ''} HEALING other survivor with MEDKIT ({actionDuration} seconds).")
                elif line[:32] == "Interaction: Verbose: [HealOther":
                    actionDuration = self.getActionDuration(lineNum)
                    if actionDuration:
                        numSurvivors = int(line[32])
                        print(f"   {numSurvivors} survivor{'s' if numSurvivors > 1 else ''} HEALING other survivor ({actionDuration} seconds).")
                elif line[:40] == "Interaction: Verbose: [SelfHealNoMedkit]":
                    actionDuration = self.getActionDuration(lineNum)
                    if actionDuration:
                        print(f"   Survivor SELF-CARING ({actionDuration} seconds).")
                elif line[:42] == "Interaction: Verbose: [SelfHealWithMedkit]":
                    actionDuration = self.getActionDuration(lineNum)
                    if actionDuration:
                        print(f"   Survivor using MEDKIT to HEAL self ({actionDuration} seconds).")     # TODO: test canceling/finishing heal




                elif line[:36] == "Interaction: Verbose: [CleanseTotem]":  # TODO: [BP_TotemBase_C_0]
                    if line.endswith("[<== Interaction Exit]"):
                        print('   ...Survivor no longer cleansing TOTEM.')
                    elif line.endswith("[<!> Charge Complete Received]"):
                        print('   ...Survivor finished cleansing TOTEM.')


                elif line[:34] == "Interaction: Verbose: [OpenEscape]":
                    if line.endswith("[<== Interaction Exit]"):
                        print(' ? Survivor has stopped opening an EXIT GATE.')
                    elif line.endswith("[<!> Charge Complete Received]"):
                        print(' ? Survivor has fully opened an EXIT GATE.')


                if "Requested to Play: " in line:       # TODO: consolodate actionDuration?
                    actionRequest = line[line.find("Requested to Play: ")+19:]
                    actionDuration = 0


                    if actionRequest[:10] == "EscapeOpen":
                        actionDuration = self.getActionDuration(lineNum)
                        print(f" ? Survivor is opening an EXIT GATE ({actionDuration} seconds).")   # TODO: killer opening the exit gate?

                    elif actionRequest[:15] == "TotemCleanse_In":
                        print('   Survivor attempting to cleanse TOTEM...')
                    elif actionRequest[:19] == "TotemCleanse_Middle":
                        actionDuration = self.getActionDuration(lineNum)
                        print(f'     ...TOTEM cleanse started ({actionDuration} seconds).')

                    elif actionRequest[:9] == "ChestOpen":
                        openType = actionRequest[9:17]
                        if openType == "_OutSucc":
                            print('...Survivor successfully finished searching CHEST.')
                        elif openType == "_OutFail":
                            print('...Survivor has cancelled CHEST search.')
                        else:
                            actionDuration = self.getActionDuration(lineNum)
                            print(f' ? Survivor searching CHEST ({actionDuration} seconds).')


                    elif actionRequest[:11] == "HookCamper ":
                        actionDuration = self.getActionDuration(lineNum)
                        if actionDuration:
                            print(f'   Killer is HOOKING survivor ({actionDuration} seconds)...')


                    elif actionRequest[:8] == "UnhookIn" and not line.endswith("AnimTag_Follower."):
                        actionDuration = self.getActionDuration(lineNum)
                        if actionDuration:
                            print(f'   Survivor is being UNHOOKED ({actionDuration} seconds)...')

                    elif actionRequest[:9] == "UnhookOut" and line.endswith("AnimTag_Follower."):
                        print('   ...Survivor has been UNHOOKED.')      # TODO: figure out unhook cancel/failure


                    elif actionRequest[:15] == "SurvivorPickup " and line[:22] == ("AnimLeader: BP_Slasher"):
                        actionDuration = self.getActionDuration(lineNum)
                        print(f"   Killer is PICKING UP survivor ({actionDuration} seconds)...")    # TODO: 16 second wiggle timer?

                    elif actionRequest[:6] == "Wiggle":
                        actionDuration = self.getActionDuration(lineNum)
                        if actionDuration:
                            print(f"   ...Survivor has started WIGGLING ({actionDuration} seconds).")



                    elif actionRequest[:9] == "PlankStun":
                        actionDuration = self.getActionDuration(lineNum)
                        print(f" ? Killer has been stunned by a PALLET ({actionDuration} seconds).")
                    elif actionRequest[:12] == "PlankDestroy":                  # TODO: nurse?
                        actionDuration = self.getActionDuration(lineNum)
                        print(f" ? Killer is breaking a PALLET ({actionDuration} seconds).")
                    elif actionRequest[:13] == "PlankPulldown":
                        print(" ? Survivor has dropped a PALLET.")


                    elif actionRequest[:11] == "WindowVault":
                        actionDuration = self.getActionDuration(lineNum)
                        if line[:21] == "AnimLeader: BP_Camper" and actionDuration:
                            vaultType = actionRequest[11:15]
                            if vaultType == "Fast":
                                print(f' ? Survivor fast-vaulting WINDOW ({actionDuration} seconds).')
                            elif vaultType == "Mid ":     # TODO: why does this vary from 0.93-1.0?
                                print(f' ? Survivor medium-vaulting WINDOW ({actionDuration} seconds).')
                            else:
                                print(f' ? Survivor slow-vaulting WINDOW ({actionDuration} seconds).')      # TODO: is this always 1.05? (plus -1 bug)
                        else:
                            if 0 < actionDuration < 1.7 and self.killer not in ('Michael Myers', 'Legion'):     # TODO: finish this for myers + legion
                                print(f' ? Killer vaulting with BAMBOOZLE ({actionDuration} seconds).')
                            else: print(f' ? Killer vaulting ({actionDuration} seconds).')
                    elif actionRequest[:10] == "PlankVault":
                        actionDuration = self.getActionDuration(lineNum)
                        if actionRequest[10:14] == "Fast":
                            print(f' ? Survivor fast-vaulting PALLET ({actionDuration} seconds).')
                        else:
                            print(f' ? Survivor slow-vaulting PALLET ({actionDuration} seconds).')



                    elif actionRequest[:11] == "LockerEnter":   # TODO: should these be consolidated?
                        if actionRequest[11:15] == "Fast":
                            print(' ? Survivor fast-entering LOCKER.')
                        else:
                            print(' ? Survivor slow-entering LOCKER.')
                    elif actionRequest[:10] == "LockerExit":
                        if actionRequest[10:14] == "Fast":
                            print(' ? Survivor fast-exiting LOCKER.')
                        else:
                            print(' ? Survivor slow-exiting LOCKER.')
                    elif actionRequest[:17] == "LockerSearchEmpty":
                        actionDuration = self.getActionDuration(lineNum)
                        print(f' ? Killer searching empty LOCKER ({actionDuration} seconds).')
                    elif actionRequest[:16] == "LockerSearchFull":
                        actionDuration = self.getActionDuration(lineNum)
                        print(f' ? Killer grabbing survivor from LOCKER ({actionDuration} seconds).')






            elif line == "LogExit: Exiting.":
                self.gameIsOpen = False
                self.showHistory = False
                print('\nDead By Daylight has been closed, checking for new log in 15 seconds.')  # TODO finish this using timestamps



    def startLogReader(self):
        while True:
            print('Checking for active logs...')
            with open(self.logPath, encoding='utf-8') as self.logFile:
                self.gameIsOpen = True

                self.log = self.logFile.readlines()
                if self.showHistory:
                    self.showingHistory = True
                    print(f'Parsing log file...\n\nHistory:\n{"-"*50}')     # add exception here
                    self.parseLog()
                    print(f'{"-"*50}\n')
                self.showingHistory = False

                while self.gameIsOpen:
                    time.sleep(0.33)
                    self.lastPosition = self.logFile.tell()
                    self.log = self.logFile.readlines()
                    self.parseLog()
            time.sleep(15)
###########################################


if __name__ == "__main__":
    dbd = DBDInstance(dbdLogPath)
    dbd.startLogReader()




#LogScaleformUI: Display: Scaleform Log: [FLASH][DEBUG] HudScreen: DBDL-22610 Investigation: HudView::ShowSkillCheck(keyType=mouse, keyText=M3, hitAreaStart=0.3797366321086884, hitAreaLength=0.13000002503395, bonusAreaLength=0.02999999932944775, isHexed=false, xOffset=0, yOffset=0)
#AnimLeader: BP_CamperFemale01_Character_C_0 Requested to Play: HitInjuredToCrawlB AnimTag_Female.
#LogSM: [BP_CamperMale01_C_0][CLIENT MASTER] <Exiting state Intro>
    #LogSM: [BP_CamperMale01_C_0][CLIENT MASTER] <Entering state Playing>
    #LogSM: [BP_CamperMale01_C_0][CLIENT MASTER] <Entering state Navigation>
    #LogScaleformUI: Display: Scaleform Log: [FLASH][DEBUG] HudScreen: DBDL-9734 Investigation: HudView::fadeOutStartSequence started -> _startSequenceComponent.alpha = 1
    #AnimLeader: Entity_GEN_VARIABLE_BP_GeneratorEntity_C_CAT_6 Requested to Play: EntityGeneratorBlock None.   # corrupt/thrilling/endgame/whatever
    #AnimLeader: Entity_GEN_VARIABLE_BP_GeneratorEntity_C_CAT_4 Requested to Play: EntityGeneratorBlock None.
    #AnimLeader: Entity_GEN_VARIABLE_BP_GeneratorEntity_C_CAT_3 Requested to Play: EntityGeneratorBlock None.
#GameFlow: Warning: UMatchHandler::LogCurrentLoadout - Loadout for F1F8160501001001
    #GameFlow: Warning: LogCurrentLoadout: Item: Item_Camper_CommodiousToolbox Addon1: _EMPTY_ Addon2: _EMPTY_ Perk1: Prove_Thyself 2 Perk2: BorrowedTime 2 Perk3: DeadHard 0 Perk4: WereGonnaLiveForever 2 Offering: _EMPTY_
    #GameFlow: Verbose: vvv OnLeavingOnlineMultiplayer vvv
    #GameFlow: Local_WriteGameEndStats IsLocalController
#GameFlow: Writing Profile Stat DBD_CamperNewItem: 1
#Interaction: Verbose: [GeneratorDamage1][GeneratorStandard_C_2] - [BP_Slasher_Character_03_C_0 - Thanquol][CLIENT SLAVE] - [<!> Charge Complete Received]
#AnimLeader: BP_Slasher_Character_14_C_0 Requested to Play: Attack_Slash_Miss Legion.
#AnimLeader: BP_Entity_C_8 Requested to Play: HookSacrificeIn AnimTag_Follower.
#Interaction: Verbose: [CollectItem][BP_Medkit_001_C_0] - [BP_CamperFemale03_Character_C_0 - Hungeredowl][CLIENT SLAVE] - [<!> Interaction Event OnInteractionUpdateStart]
    #AnimLeader: BP_CamperFemale03_Character_C_0 Requested to Play: ItemCollect AnimTag_Female.
#LogSM: Error: Play Update Montage AM_TT_SetBearTrap_ACTION Duration 1.500000 Timestamp 0.000000
#GameFlow: LoadingContextComponent::StartLoadingTask - Begin level loading - TransitionId=LOADING_TRAVELING_JOINING_LOBBY (6)
#GameFlow: LoadingContextComponent::Enter - TransitionId=LOADING_TRAVELING_TO_OFFLINE_LOBBY (2)
#GameFlow: LoadingContextComponent::Leave - TransitionId=LOADING_TRAVELING_TO_OFFLINE_LOBBY (2)

#GameFlow: [PartyContextComponent::CheckStartMatch] matchmakingState : 1, isQuickmatching : 1
#GameFlow: [PartyContextComponent::UpdateReadyButtonStateInfo] Ready button updated : 1.
#Interaction: Player [BP_CamperFemale02_Character_C_0] is not in chase anymore.
#LogScaleformUI: Display: Scaleform Log: [FLASH][INFO] PlayerStatusController: AddPlayer: playerIndex=1 playerId:76561198052790148 playerName:Mike Rotchburns isLocalPlayer:false playerStatus:8 playerObsessionState:0 isBroken:false

#[2020.05.18-01.45.06:995][217]GameFlow: OfferingContextComponent::SendOfferingsDataToUI --> Sending to UI offering Survivor Pudding
#[2020.05.18-01.45.06:995][217]GameFlow: OfferingContextComponent::SendOfferingsDataToUI --> Keep in cache offering Survivor Pudding