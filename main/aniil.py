# main/aniil.py
import time as Time
from pathlib import Path
_data_folder = Path('data/')
_data_folder.mkdir(parents=True, exist_ok=True)

class ANIIL:
    def __init__(self, targetgameid: int, data: tuple) -> None:
        'For new game: targetgameid=None, input settings as data. For existing game: input targetgameid, data=None.'
        self.file = None
        if targetgameid is None:
            self.gameid = self.findUniqueID()
            if self.gameid == 0:
                print('<ANIIL MODULE> Memory for games full.')
            else:
                self.lognum = 1
                self.initFile(data)
        else:
            self.gameid = targetgameid
            self.lognum = 1
    
    def findUniqueID(self) -> int:
        'Finds unique game ID.'
        for i in range(99):
            _target_file = _data_folder / f'{str(i+1)}.aniil'
            if not _target_file.is_file():
                return i+1
        # Memory for games is full
        return 0

    def initFile(self, data) -> None:
        'Responsible for writing initial data to top of file.'
        local_time = Time.localtime()
        time = f'{local_time[3]}:{local_time[4]}:{local_time[5]}'
        date = f'{local_time[2]}.{local_time[1]}.{local_time[0]}'
        data_to_write = f'ID: #{self.gameid}\nLOCALTIME: {time}, {date}\nSETTINGS: {data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[5]}\nFEN: {data[4]}\nMOVELOG:\n'
        _target_file = _data_folder / f'{str(self.gameid)}.aniil'
        with _target_file.open('w', encoding='utf-8') as file:
            file.write(data_to_write)
            file.close()
    
    def writeLog(self, log) -> None:
        'Responsible for writing data to gameid.aniil.'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('a', encoding='utf-8') as file:
            file.write(f'{self.lognum}. {log}\n')
            self.lognum += 1
            file.close()
    
    def finishGame(self) -> None:
        'Responsible for putting data into a finished game format.'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('r', encoding='utf-8') as file:
            lines = file.readlines()
            settings = lines[2]
            settings = settings.split(',')
            settings[0] = 'True'
            settings = ','.join(settings)
            file.close()
        to_replace_with = f'SETTINGS: {settings}'
        self.replaceLineWith(3, to_replace_with)
        with _target_file.open('a', encoding='utf-8') as file:
            file.write('///')
            file.close()
    
    def updateFEN(self, newfen) -> None:
        'Updates the fen string of the game.'
        to_replace_with = f'FEN: {newfen}\n'
        self.replaceLineWith(4, to_replace_with)

    def replaceLineWith(self, line, data) -> None:
        'Replaces specified line with data input.'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('r', encoding='utf-8') as file:
            lines = file.readlines()
            file.close()
        lines[line-1] = data
        with _target_file.open('w', encoding='utf-8') as file:
            file.writelines(lines)
            file.close()
    
    def deleteSelf(self) -> None:
        'Deletes current ANIIL file.'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        _target_file.unlink()

    def setSaved(self, bool=True) -> None:
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('r', encoding='utf-8') as file:
            lines = file.readlines()
            settings = lines[2]
            settings = settings.split(',')
            if bool:
                settings[4] = 'True'
            else:
                settings[4] = 'False'
            settings = ','.join(settings)
            file.close()
        to_replace_with = f'SETTINGS: {settings}'
        self.replaceLineWith(3, to_replace_with)

    # Public access methods ///

    def getGameID(self) -> int:
        'Returns this object\'s unique game ID.'
        return int(self.gameid)
    
    def getLocalTime(self) -> tuple[str]:
        'Returns LOCALTIME of when this game was first init as: (HH.MM.SS, DD.MM.YYYY)'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('r', encoding='utf-8') as file:
            lines = file.readlines()
            file.close()
        localtime = lines[1][11:]
        localtime = localtime.split(',')
        time = localtime[0]
        date = localtime[1][1:]
        date = date.split('\n')
        return (time, date[0])
    
    def getSettings(self) -> tuple[str]:
        'Returns SETTINGS of this game, excluding FEN. Settings in format: (completed?, gamestate, enginedepth (0 being no engine), timelimit).'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('r', encoding='utf-8') as file:
            lines = file.readlines()
            file.close()
        settings = lines[2][10:]
        settings = settings.split(',')
        saved = settings[4][1:]
        saved = saved.split('\n')
        return (settings[0], settings[1][1:], settings[2][1:], settings[3][1:], saved[0])
    
    def getFEN(self) -> str:
        'Returns FEN string of game.'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('r', encoding='utf-8') as file:
            lines = file.readlines()
            file.close()
        fen = lines[3][5:]
        fen = fen.split('\n')
        return fen[0]
    
    def getLogs(self) -> list[str]:
        'Returns list of logs, where log line in the format \'e6/e7\'.'
        _target_file = _data_folder / f'{self.gameid}.aniil'
        with _target_file.open('r', encoding='utf-8') as file:
            lines = file.readlines()
            file.close()
        templogs = lines[5:]
        logs = []
        for templog in templogs:
            if (templog == '///') or (templog == ''):
                break
            log = templog[3:]
            log = log.split('\n')
            logs.append(log[0])
        return logs

# ---

def getAllIDS() -> list[str]:
    'Returns list of all used ID\'s as strings.'
    ids = []
    for i in range(99):
        _target_file = _data_folder / f'{str(i+1)}.aniil'
        if _target_file.is_file():
            ids.append(str(i+1))
    return ids