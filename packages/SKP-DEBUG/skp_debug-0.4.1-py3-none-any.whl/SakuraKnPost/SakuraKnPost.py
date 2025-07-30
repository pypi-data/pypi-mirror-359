from pip._internal import main as _main
import importlib
import csv
def _import(name, module, ver=None):
    try:
        globals()[name] = importlib.import_module(module)
    except ImportError:
        try:
            if ver is None:
                _main(['install', module])
            else:
                _main(['install', '{}=={}'.format(module, ver)])
            globals()[name] = importlib.import_module(module)
        except:
            print("can't import: {}".format(module))

_import('requests','requests')
import requests
import tempfile
class _Const:
    class ConstError(TypeError): pass
    
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError(f"定数を上書きしようとしています: {name}")
        self.__dict__[name] = value

const = _Const()
const.version = 0.4
const.url = "http://10.146.80.98/dataIO/DataSave.php"
CSVconst = _Const()
Created = False
def __Send(CSVdata):
    with tempfile.NamedTemporaryFile(mode="w+",newline="",encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerows(CSVdata)
        fp.seek(0)
        files = {
            "Field" : ("data.csv",fp,"text/csv"),
        }
        data = {
            "version" : const.version,
        }
        response = requests.post(const.url,files=files,data=data)
    	
    #print(response.status_code)
    response_text = response.text.replace("<br>","\n")
    return response_text


def Create(measurement :str):
    global Created
    if Created == True:
        print("Creat()が二回実行されました。\n Create()を一個だけにするか、先にRelease()を実行してください\n このCreate()は無視されます。")
        return
    Created = True
    CSVconst.measurement = measurement
    CSVconst.data = [["MEASUREMENT",measurement]]


def Send(**Kwargs):
    data = CSVconst.data.copy()
    #print(data)
    for k in Kwargs:
        row = [k,Kwargs[k]]
        data.append(row)
    data = [list(x) for x in zip(*data)]
    return __Send(data)


def Release():
    global CSVconst,Created
    CSVconst = _Const()
    Created = False
    
def Version():
	return const.version