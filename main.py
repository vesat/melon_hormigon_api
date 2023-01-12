
from typing import Optional

from dotenv import load_dotenv
import os
from fastapi import FastAPI
import requests
import xmltodict, json
import pandas as pd
from dotenv import load_dotenv
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))
ENV_VARS = os.path.join(BASEDIR, ".env")
# se cargan las variables de entorno
load_dotenv(ENV_VARS)
########################
host_api = os.environ.get('ip_api')



app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/planta/{id}")
def read_item(id: int, q: Optional[str] = None):
    print(f" la planta solicitada es {id}")

    lista_plantas=[121,122,123,124,131,132,133]

    ##la planta solicitada no existe
    if id not in lista_plantas:
        camiones = {
            "camiones": ["0"],
            "hora": [""],
            "hora_cam": ["0"],
            "estado": ["2"]
        }
        tabla_camiones = pd.DataFrame(camiones)
        json_tabla = tabla_camiones.to_json(orient='columns')
        return json_tabla

    consulta=f'http://{host_api}/Atcom/ws_Letrero/WSLetrerov2.asmx/Data?IDEjecucion=Edu2060Letrero&Planta={id}'
    print(consulta)

    r = requests.get(consulta)

    obj = xmltodict.parse(r.text)  # <class 'collections.OrderedDict'>
    salida = json.dumps(obj)
    datos = True
    print("---")
    salida_dict = dict(obj)
    # print(salida_dict.keys())

    salida_dict_2 = salida_dict['DataTable']

    del salida_dict_2['@xmlns']
    del salida_dict_2['xs:schema']
    ##con lo anterior queda solo el "diffgr:diffgram", ver comparacion de todo estos datos en

    salida_dict_3 = salida_dict_2['diffgr:diffgram']

    ## si no vienen camiones, los keys son odict_keys(['@xmlns:msdata', '@xmlns:diffgr'])
    ## si vienen son  odict_keys(['@xmlns:msdata', '@xmlns:diffgr', 'DocumentElement']) ##con camiones

    if 'DocumentElement' in salida_dict_3:
        # print("tiene Document")
        if 'QUERY CMD SIN DATOS' in salida:  # aca busco si existe la palabra
            print("---------------no existen camiones QUERY CMD SIN DATOS")
            try:
                datos = False
                trama = "B0 0;0 0;0 0;0 0;0 0;0 0;0 0;0 0E"

                print(f" {id}  {trama}")
                camiones = {
                    "camiones": ["0"],
                    "hora": [""],
                    "hora_cam": ["0"],
                    "estado": ["3"]
                }
                tabla_camiones = pd.DataFrame(camiones)
                json_tabla = tabla_camiones.to_json(orient='columns')
                return json_tabla

            except:
                ####TODO enviar log
                pass
        else:
            # print("existen camiones")
            datos = True
    else:
        # print("Sin documents,por lo que no tiene camion")
        datos = False
        trama = "B0 0;0 0;0 0;0 0;0 0;0 0;0 0;0 0E"
        print(f" {id}  {trama}")
        camiones = {
            "camiones": ["0"],
            "hora": [""],
            "hora_cam": ["0"],
            "estado": ["4"]
        }
        tabla_camiones = pd.DataFrame(camiones)
        json_tabla = tabla_camiones.to_json(orient='columns')
        return json_tabla

    ##solo deberia entrar si existen camiones
    if datos:
        salida_dict_4 = salida_dict_3['DocumentElement']
        salida_dict_5 = salida_dict_4['TablaLetrero']
        num_camiones = len(salida_dict_5)
        lista_camiones = []
        print("+"*100)
        print(salida_dict_5)
        print("-"*100)
        print(f"numero de camionbes {num_camiones}")
        #TODO el error se produce cuando el numero de camiones es ugual o mayor a 5

        # print(f"variable {num_camiones}  ,planta {planta}")
        if num_camiones > 10 and datos:  ##el largo es 37 ya que como es solo un camion, lo pasa a una lista, es del tipo <class 'collections.OrderedDict'>
            # print("un camion")
            lista_camiones.append(salida_dict_5)
        elif num_camiones == 2 and datos:
            # print("tiene 2 camiones")
            lista_camiones = salida_dict_5
        elif num_camiones == 3 and datos:
            # print("tiene 3 camiones")
            lista_camiones = salida_dict_5

        elif num_camiones == 4 and datos:
            # print("tiene 4 camiones")
            lista_camiones = salida_dict_5

        elif num_camiones == 5 and datos:
            # print("tiene 4 camiones")
            lista_camiones = salida_dict_5
        elif num_camiones == 6 and datos:
            # print("tiene 4 camiones")
            lista_camiones = salida_dict_5
        elif num_camiones == 7 and datos:
            # print("tiene 4 camiones")
            lista_camiones = salida_dict_5
        elif not datos:
            # print("sin camiones")
            lista_camiones = []
        else:
            #  print("no se reconocieron los datos")
            # TODO generar un log o insert en base de datos
            pass

        ##ordenar port '@diffgr:id',
        df = pd.DataFrame(lista_camiones)
        df.sort_values(by = '@diffgr:id',inplace=True)

        camiones = {
            "camiones": ["0"],
            "hora": [""],
            "hora_cam": ["0"],
            "estado": ["5"]
        }
        tabla_camiones = pd.DataFrame(camiones)

        ##un datafram completo
        for index, row  in df.iterrows():
            print(f"---{row['CODIGO_CAMION']}----")
            tabla_camiones = tabla_camiones.append({f'camiones': row['CODIGO_CAMION'], 'hora_cam':row['HORA_IMPRESO_GUIA'],'hora': '4', 'estado': '5'}, ignore_index=True)
        print(tabla_camiones)
        json_tabla = tabla_camiones.to_json(orient='columns')
        print("envia con camionex")
        return json_tabla

    ##voy a armar un datframa para envia






