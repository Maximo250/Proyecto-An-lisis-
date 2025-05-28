# -*- coding: utf-8 -*-
# Se instalan los paquetes y librerías a utilizar en el programa
#pip install pandas
#pip install numpy
#pip install tabulate

import pandas as pd
import numpy as np
from tabulate import tabulate

# Todas las bases de datos de la ENIGH 2022 deben estar en formato CSV

# En este programa se utilizan las siguientes bases, 
# nombrándolas de la siguiente forma:

# Base de población: poblacion.csv
# Base de trabajos: trabajos.csv
# Base de ingresos: ingresos.csv
# Base de viviendas: viviendas.csv
# Base de hogares: hogares.csv
# Base de concentrado: concentradohogar.csv
# Base de no monetario hogar: gastoshogar.csv
# Base de no monetario personas: gastospersona.csv

# En este programa de cálculo se utilizan dos tipos de archivos, los cuales 
# están ubicados en las siguientes carpetas:

# 1) Bases originales: 'C:/Pobreza 2022/Bases de datos'
# 2) Bases generadas:  'C:/Pobreza 2022/Bases'

import os
os.chdir('C:/Pobreza_2022')
os.getcwd()

################################################################################
#
# PROGRAMA DE CÁLCULO PARA LA MEDICIÓN MULTIDIMENSIONAL DE LA POBREZA* 2022
#
################################################################################
# De acuerdo con los Lineamientos y criterios generales para la definición, identificación y 
# medición de la pobreza (2018) que se pueden consultar en el Diario Oficial de la Federación 
# (https://www.dof.gob.mx/nota_detalle.php?codigo=5542421&fecha=30/10/2018) y la Metodología 
# para la medición multidimensional de la pobreza en México, tercera edición 
# (https://www.coneval.org.mx/InformesPublicaciones/InformesPublicaciones/Documents/Metodo
# logia-medicion-multidimensional-3er-edicion.pdf).
################################################################################

################################################################################
# Parte I Indicadores de carencias sociales:
# INDICADOR DE REZAGO EDUCATIVO
################################################################################

pobla = pd.read_csv('Bases de datos/poblacion.csv', low_memory=False)
rezedu = pobla.copy()

#Convirtiendo variables string a numericas
rezedu[['parentesco','edad','asis_esc','nivelaprob','gradoaprob','antec_esc','hablaind']
       ]=rezedu[['parentesco','edad','asis_esc','nivelaprob','gradoaprob','antec_esc','hablaind']].apply(pd.to_numeric, errors='coerce')

# Población objetivo: no se incluye a huéspedes ni trabajadores domésticos
rezedu = rezedu[~((rezedu['parentesco'] >= 400) & (rezedu['parentesco'] < 500) |
                  (rezedu['parentesco'] >= 700) & (rezedu['parentesco'] < 800))]

# Año de nacimiento
rezedu['anac_e'] = 2022 - rezedu['edad'].fillna(0)

# Inasistencia escolar (se reporta para personas de 3 años o más)
rezedu['inas_esc'] = np.NAN
rezedu.loc[(rezedu['asis_esc'] == 1), 'inas_esc'] = 0 # Sí asiste
rezedu.loc[(rezedu['asis_esc'] == 2), 'inas_esc'] = 1 # No asiste

# Nivel educativo
rezedu['niv_ed'] = np.NAN
#Con primaria incompleta o menos
rezedu.loc[(rezedu['nivelaprob'] < 2) | ((rezedu['nivelaprob'] == 2) & (rezedu['gradoaprob'] < 6)), 'niv_ed'] = 0
# Primaria completa o secundaria incompleta
rezedu.loc[((rezedu['nivelaprob'] == 2) & (rezedu['gradoaprob'] == 6)) |
           ((rezedu['nivelaprob'] == 3) & (rezedu['gradoaprob'] < 3)) |
           (((rezedu['nivelaprob'] == 5) | (rezedu['nivelaprob'] == 6)) & (rezedu['gradoaprob'] < 3) & (rezedu['antec_esc'] == 1)), 'niv_ed'] = 1
# Secundaria completa o media superior incompleta
rezedu.loc[((rezedu['nivelaprob'] == 3) & (rezedu['gradoaprob'] == 3)) |
           ((rezedu['nivelaprob'] == 4) & (rezedu['gradoaprob'] < 3)) |
           ((rezedu['nivelaprob'] == 5) & (rezedu['antec_esc'] == 1) & (rezedu['gradoaprob'] >= 3)) |
           ((rezedu['nivelaprob'] == 6) & (rezedu['antec_esc'] == 1) & (rezedu['gradoaprob'] >= 3)) |
           ((rezedu['nivelaprob'] == 5) & (rezedu['antec_esc'] == 2) & (rezedu['gradoaprob'] < 3)) |
           ((rezedu['nivelaprob'] == 6) & (rezedu['antec_esc'] == 2) & (rezedu['gradoaprob'] < 3)), 'niv_ed'] = 2
# Media superior completa o mayor nivel educativo
rezedu.loc[((rezedu['nivelaprob'] == 4) & (rezedu['gradoaprob'] == 3)) |
           ((rezedu['nivelaprob'] == 5) & (rezedu['antec_esc'] == 2) & (rezedu['gradoaprob'] >= 3)) |
           ((rezedu['nivelaprob'] == 6) & (rezedu['antec_esc'] == 2) & (rezedu['gradoaprob'] >= 3)) |
           ((rezedu['nivelaprob'] == 5) & (rezedu['antec_esc'] > 2)) |
           ((rezedu['nivelaprob'] == 6) & (rezedu['antec_esc'] > 2)) |
           ((rezedu['nivelaprob'] >= 7) & (~rezedu['nivelaprob'].isna())), 'niv_ed'] = 3

# Indicador de carencia por rezago educativo
################################################################################
# Se considera en situación de carencia por rezago educativo 
# a la población que cumpla con alguno de los siguientes criterios:
#
# 1. Tiene de tres a 21 años, no cuenta con la educación
#    obligatoria y no asiste a un centro de educación formal.
# 2. Tiene 22 años o más, nació a partir del año 1998 y no ha terminado 
#    la educación obligatoria (media superior).
# 3. Tiene 16 años o más, nació entre 1982 y 1997 y no cuenta con el
#    nivel de educación obligatorio vigente en el momento en que debía  
#    haberlo cursado (secundaria completa).
# 4. Tiene 16 años o más, nació antes de 1982 y no cuenta con el nivel 
#    de educación obligatorio vigente en el momento en que debía haberlo 
#    cursado (primaria completa).	
################################################################################

rezedu['ic_rezedu'] = np.NAN
rezedu.loc[(rezedu['anac_e'] >= 1998) & (rezedu['edad'].between(3, 21)) &
           (rezedu['inas_esc'] == 1) & (rezedu['niv_ed'] < 3), 'ic_rezedu'] = 1 # Presenta carencia
rezedu.loc[((rezedu['anac_e'] >= 1982) & (rezedu['anac_e'] <= 1997)) &
           (rezedu['edad'] >= 16) & (rezedu['niv_ed'] < 2), 'ic_rezedu'] = 1 # Presenta carencia
rezedu.loc[(rezedu['anac_e'] <= 1981) & (rezedu['edad'] >= 16) & (rezedu['niv_ed'] == 0), 'ic_rezedu'] = 1 # Presenta carencia
rezedu.loc[(rezedu['anac_e'] >= 1998) & (rezedu['edad'] >= 22) & (rezedu['niv_ed'] < 3), 'ic_rezedu'] = 1 # Presenta carencia
rezedu.loc[(rezedu['edad'].between(0, 2)), 'ic_rezedu'] = 0 # No presenta carencia
rezedu.loc[(rezedu['anac_e'] >= 1998) & (rezedu['edad'].between(3, 21)) & (rezedu['inas_esc'] == 0), 'ic_rezedu'] = 0 # No presenta carencia
rezedu.loc[(rezedu['niv_ed'] == 3), 'ic_rezedu'] = 0 # No presenta carencia
rezedu.loc[((rezedu['anac_e'] >= 1982) & (rezedu['anac_e'] <= 1997)) & (rezedu['edad'] >= 16) &
           ((rezedu['niv_ed'] >= 2) & (~rezedu['niv_ed'].isna())), 'ic_rezedu'] = 0 # No presenta carencia
rezedu.loc[(rezedu['anac_e'] <= 1981) & (rezedu['edad'] >= 16) &
           ((rezedu['niv_ed'] >= 1) & (~rezedu['niv_ed'].isna())), 'ic_rezedu'] = 0 # No presenta carencia

# Hablante de lengua indígena
rezedu['hli'] = np.NAN
rezedu.loc[(rezedu['hablaind'] == 1) & (rezedu['edad'] >= 3), 'hli'] = 1 # Habla lengua indígena
rezedu.loc[(rezedu['hablaind'] == 2) & (rezedu['edad'] >= 3), 'hli'] = 0 # No habla lengua indígena

rezedu = rezedu[['folioviv', 'foliohog', 'numren', 'edad', 'anac_e', 'inas_esc', 'niv_ed',
                 'ic_rezedu', 'parentesco', 'hli']]

rezedu.to_csv('Bases/ic_rezedu22.csv', index=False)

################################################################################
# Parte II Indicadores de carencias sociales:
# INDICADOR DE CARENCIA POR ACCESO A LOS SERVICIOS DE SALUD
################################################################################

# Acceso a servicios de salud por prestaciones laborales
ocupados = pd.read_csv('Bases de datos/trabajos.csv', low_memory=False)
#Convirtiendo variables string a numericas
ocupados[['subor', 'indep', 'tiene_suel','pago','id_trabajo']]=ocupados[['subor', 'indep', 'tiene_suel','pago','id_trabajo']].apply(pd.to_numeric, errors='coerce')

# Tipo de trabajador: identifica la población subordinada e independiente
ocupados['tipo_trab'] = np.NAN
# Subordinados
ocupados.loc[(ocupados['subor'] == 1), 'tipo_trab'] = 1
# Independientes que reciben un pago
ocupados.loc[(ocupados['subor'] == 2) & (ocupados['indep'] == 1) & (ocupados['tiene_suel'] == 1), 'tipo_trab'] = 2
ocupados.loc[(ocupados['subor'] == 2) & (ocupados['indep'] == 2) & (ocupados['pago'] == 1), 'tipo_trab'] = 2
#Independientes que no reciben un pago
ocupados.loc[(ocupados['subor'] == 2) & (ocupados['indep'] == 1) & (ocupados['tiene_suel'] == 2), 'tipo_trab'] = 3
ocupados.loc[(ocupados['subor'] == 2) & (ocupados['indep'] == 2) & ((ocupados['pago'] == 2) | (ocupados['pago'] == 3)), 'tipo_trab'] = 3

# Ocupación principal o secundaria
ocupados['ocupa'] = np.NAN
ocupados.loc[(ocupados['id_trabajo'] == 1), 'ocupa'] = 1
ocupados.loc[(ocupados['id_trabajo'] == 2), 'ocupa'] = 1

ocupados = ocupados[['folioviv', 'foliohog', 'numren', 'id_trabajo', 'tipo_trab', 'ocupa']]

# Distinción de prestaciones en trabajo principal y secundario
ocupados = pd.pivot_table(ocupados, index=['folioviv', 'foliohog', 'numren'], columns='id_trabajo', 
                          values=['tipo_trab', 'ocupa'], aggfunc=np.sum, fill_value=0)
ocupados.columns = [f'{i}{j}' for i, j in ocupados.columns]
ocupados = ocupados.reset_index()

# Identificación de la población trabajadora 
# (toda la que reporta al menos un empleo en la base de trabajos.csv)
ocupados['trab'] = 1
ocupados = ocupados[['folioviv', 'foliohog', 'numren', 'trab'] + [col for col in ocupados.columns if col.startswith('tipo_trab') or col.startswith('ocupa')]]
ocupados.to_csv('Bases/ocupados22.csv', index=False)

# Población objetivo: no se incluye a huéspedes ni trabajadores domésticos
salud = pobla.copy()
salud = salud.loc[~((salud['parentesco'] >= 400) & (salud['parentesco'] < 500) |
                    (salud['parentesco'] >= 700) & (salud['parentesco'] < 800))]

salud = pd.merge(salud, ocupados, on=['folioviv', 'foliohog', 'numren'], how='left')

#Convirtiendo variables string a numericas
salud[['parentesco', 'trab', 'edad', 'act_pnea1', 'act_pnea2','ocupa1', 'atemed', 
       'inst_1', 'inst_2', 'inst_3', 'inst_4', 'inst_5', 'inst_6', 
       'inscr_1', 'inscr_2', 'inscr_3', 'inscr_4', 'inscr_5', 'inscr_6', 'inscr_7', 'asis_esc', 'pop_insabi', 'segvol_2']
      ] = salud[['parentesco', 'trab', 'edad', 'act_pnea1', 'act_pnea2','ocupa1', 'atemed', 
                 'inst_1', 'inst_2', 'inst_3', 'inst_4', 'inst_5', 'inst_6', 
                 'inscr_1', 'inscr_2', 'inscr_3', 'inscr_4', 'inscr_5', 'inscr_6', 'inscr_7', 'asis_esc', 'pop_insabi', 'segvol_2']].apply(pd.to_numeric, errors='coerce')

# PEA (personas de 16 años o más)
salud['pea'] = np.NAN
salud.loc[(salud['trab'] == 1) & (salud['edad'] >= 16) & 
          (~salud['edad'].isna()), 'pea'] = 1 # PEA: ocupada
salud.loc[((salud['act_pnea1'] == 1) | (salud['act_pnea2'] == 1)) & 
          (salud['edad'] >= 16) & (~salud['edad'].isna()),'pea'] = 2 # PEA: desocupada
salud.loc[((salud['edad'] >= 16) & (~salud['edad'].isna()) &
         (((salud['act_pnea1'] != 1) | (salud['act_pnea1'].isna())) &
         ((salud['act_pnea2'] != 1) | (salud['act_pnea2'].isna()))) &
         (((salud['act_pnea1'] >= 2) & (salud['act_pnea1'] <= 6)) |
         ((salud['act_pnea2'] >= 2) & (salud['act_pnea2'] <= 6)))),'pea'] = 0 # PNEA
   
# Tipo de trabajo
    # Ocupación principal
salud['tipo_trab1'] = np.where(salud['pea'] == 1, salud['tipo_trab1'], salud['tipo_trab1']) # Depende de un patrón, jefe o superior 
salud['tipo_trab1'] = np.where((salud['pea'] == 0) | (salud['pea'] == 2), np.NAN, salud['tipo_trab1']) # No depende de un jefe y recibe o tiene asignado un sueldo
salud['tipo_trab1'] = np.where(salud['pea'].isna(), np.NAN, salud['tipo_trab1']) # No depende de un jefe y no recibe o no tiene asignado un sueldo
    # Ocupación secundaria
salud['tipo_trab2'] = np.where(salud['pea'] == 1, salud['tipo_trab2'], salud['tipo_trab2']) # Depende de un patrón, jefe o superior
salud['tipo_trab2'] = np.where((salud['pea'] == 0) | (salud['pea'] == 2), np.NAN, salud['tipo_trab2']) # No depende de un jefe y recibe o tiene asignado un sueldo
salud['tipo_trab2'] = np.where(salud['pea'].isna(), np.NAN, salud['tipo_trab2']) # No depende de un jefe y no recibe o no tiene asignado un sueldo

# Servicios médicos prestaciones laborales
    # Ocupación principal
salud['smlab1'] = np.NAN
salud.loc[(salud['ocupa1'] == 1), 'smlab1'] = 0 # Sin servicios médicos
salud.loc[((salud['ocupa1'] == 1) & (salud['atemed'] == 1) &
                           ((salud['inst_1'] == 1) | (salud['inst_2'] == 2) | (salud['inst_3'] == 3) | (salud['inst_4'] == 4)) & 
                           (salud['inscr_1'] == 1), 'smlab1')] = 1 # Con servicios médicos
    # Ocupación secundaria
salud['smlab2'] = np.NAN
salud.loc[(salud['ocupa2'] == 1), 'smlab2'] = 0 # Sin servicios médicos
salud.loc[((salud['ocupa2'] == 1) & (salud['atemed'] == 1) &
                           ((salud['inst_1'] == 1) | (salud['inst_2'] == 2) | (salud['inst_3'] == 3) | (salud['inst_4'] == 4)) & 
                           (salud['inscr_1'] == 1), 'smlab2')] = 1 # Con servicios médicos
    # Contratación voluntaria de servicios médicos
salud['smcv'] = np.NAN
salud.loc[((salud['edad'] >= 12) & (~salud['edad'].isna())), 'smcv'] = 0 # No cuenta
salud.loc[((salud['atemed'] == 1) &
                         ((salud['inst_1'] == 1) | (salud['inst_2'] == 2) | (salud['inst_3'] == 3) | (salud['inst_4'] == 4)) & 
                         (salud['inscr_6'] == 6) & (salud['edad'] >= 12) & (~salud['edad'].isna())), 'smcv'] = 1 # Sí cuenta

# Acceso directo a servicios de salud
salud['sa_dir'] = np.NAN
    # Ocupación principal
salud.loc[((salud['tipo_trab1'] == 1) & (salud['smlab1'] == 1)), 'sa_dir'] = 1 # Con acceso
salud.loc[((salud['tipo_trab1'] == 2) & ((salud['smlab1'] == 1) | (salud['smcv'] == 1))), 'sa_dir'] = 1 # Con acceso
salud.loc[((salud['tipo_trab1'] == 3) & ((salud['smlab1'] == 1) | (salud['smcv'] == 1))), 'sa_dir'] = 1 # Con acceso
    # Ocupación secundaria
salud.loc[((salud['tipo_trab2'] == 1) & (salud['smlab2'] == 1)), 'sa_dir'] = 1 # Con acceso
salud.loc[((salud['tipo_trab2'] == 2) & ((salud['smlab2'] == 1) | (salud['smcv'] == 1))), 'sa_dir'] = 1 # Con acceso
salud.loc[((salud['tipo_trab2'] == 3) & ((salud['smlab2'] == 1) | (salud['smcv'] == 1))), 'sa_dir'] = 1 # Con acceso
salud.loc[(salud['sa_dir'].isna()), 'sa_dir'] = 0 # Sin acceso
    # Núcleos familiares
salud['par'] = np.NAN
salud.loc[((salud['parentesco'] >= 100) & (salud['parentesco'] < 200)), 'par'] = 1 # Jefe o jefa del hogar
salud.loc[((salud['parentesco'] >= 200) & (salud['parentesco'] < 300)), 'par'] = 2 # Cónyuge del  jefe/a
salud.loc[((salud['parentesco'] >= 300) & (salud['parentesco'] < 400)), 'par'] = 3 # Hijo del jefe/a
salud.loc[((salud['parentesco'] == 601)), 'par'] = 4 # Padre o Madre del jefe/a
salud.loc[((salud['parentesco'] == 615)), 'par'] = 5 # Suegro del jefe/a
salud.loc[(salud['par'].isna()), 'par'] = 6 # Sin acceso

# Asimismo, se utilizará la información relativa a la asistencia a la escuela
salud['inas_esc'] = np.NAN
salud.loc[((salud['asis_esc'] == 1)), 'inas_esc'] = 0 # Sí asiste
salud.loc[((salud['asis_esc'] == 2)), 'inas_esc'] = 1 # No asiste

# En primer lugar se identifican los principales parentescos respecto a la 
# jefatura del hogar y si ese miembro cuenta con acceso directo
salud['jef'] = np.NAN
salud.loc[((salud['par'] == 1) & (salud['sa_dir'] == 1)), 'jef'] = 1
salud.loc[((((salud['inst_2'] == 2) | (salud['inst_3'] == 3)) & (salud['inscr_6'] == 6)) &
          ((salud['inst_1'].isna()) & (salud['inst_4'].isna()) & (salud['inst_6'].isna())) &
          ((salud['inscr_1'].isna()) & (salud['inscr_2'].isna()) & (salud['inscr_3'].isna()) &
          (salud['inscr_4'].isna()) & (salud['inscr_5'].isna()) & (salud['inscr_7'].isna()))), 'jef'] = np.NAN

salud['cony'] = np.NAN
salud.loc[((salud['par'] == 2) & (salud['sa_dir'] == 1)), 'cony'] = 1
salud.loc[((((salud['inst_2'] == 2) | (salud['inst_3'] == 3)) & (salud['inscr_6'] == 6)) &
          ((salud['inst_1'].isna()) & (salud['inst_4'].isna()) & (salud['inst_6'].isna())) &
          ((salud['inscr_1'].isna()) & (salud['inscr_2'].isna()) & (salud['inscr_3'].isna()) &
          (salud['inscr_4'].isna()) & (salud['inscr_5'].isna()) & (salud['inscr_7'].isna()))), 'cony'] = np.NAN

salud['hijo'] = np.NAN
salud.loc[((salud['par'] == 3) & (salud['sa_dir'] == 1)), 'hijo'] = 1
salud.loc[((((salud['inst_2'] == 2) | (salud['inst_3'] == 3)) & (salud['inscr_6'] == 6)) &
          ((salud['inst_1'].isna()) & (salud['inst_4'].isna()) & (salud['inst_6'].isna())) &
          ((salud['inscr_1'].isna()) & (salud['inscr_2'].isna()) & (salud['inscr_3'].isna()) &
          (salud['inscr_4'].isna()) & (salud['inscr_5'].isna()) & (salud['inscr_7'].isna()))), 'hijo'] = np.NAN

salud = salud.groupby(['folioviv', 'foliohog']).apply(lambda x: pd.Series({'jef_sa': x['jef'].sum(skipna=True),
                                                                           'cony_sa': x['cony'].sum(skipna=True),
                                                                           'hijo_sa': x['hijo'].sum(skipna=True)})).reset_index().merge(salud, on=['folioviv', 'foliohog'])

salud.loc[(salud['jef_sa'] > 0), 'jef_sa'] = 1 # Acceso directo a servicios de salud de la jefatura del hogar
salud.loc[(salud['cony_sa'] > 0), 'cony_sa'] = 1 # Acceso directo a servicios de salud del cónyuge de la jefatura del hogar
salud.loc[(salud['hijo_sa'] > 0), 'hijo_sa'] = 1 # Acceso directo a servicios de salud de hijos(as) de la jefatura del hogar

# Otros núcleos familiares: se identifica a la población con acceso a servicios de salud
# mediante otros núcleos familiares a través de la afiliación
# o inscripción a servicios de salud por algún familiar dentro o 
# fuera del hogar, muerte del asegurado o por contratación propia;

salud['s_salud'] = np.NAN
salud.loc[((~salud['pop_insabi'].isna()) & (~salud['atemed'].isna())), 's_salud'] = 0 # No cuenta
salud.loc[((salud['atemed'] == 1) & ((salud['inst_1'] == 1) | (salud['inst_2'] == 2) | (salud['inst_3'] == 3) | (salud['inst_4'] == 4)) &
          ((salud['inscr_3'] == 3) | (salud['inscr_4'] == 4) | (salud['inscr_6'] == 6) | (salud['inscr_7'] == 7))), 's_salud'] = 1 # Sí cuenta

# Indicador de carencia por servicios de salud
################################################################################
# Se considera en situación de carencia por acceso a servicios de salud
# a la población que:
#  
# 1. No se encuentra inscrita al Seguro Popular* o afiliada a alguna institución 
#    por prestación laboral, contratación voluntaria o afiliación de un 
#    familiar por parentesco directo a recibir servicios médicos por alguna
#    institución que los preste como: las instituciones de seguridad social 
#    (IMSS, ISSSTE federal o estatal, Pemex, Ejército o Marina), los servicios 
#    médicos privados, u otra institución médica.
# 
# *Se reporta la población que respondió estar afiliado o inscrito
# al Seguro Popular, o que tiene derecho a los servicios del
# Instituto de Salud para el Bienestar (INSABI), lo anterior
# de acuerdo con el cuestionario de la ENIGH 2022.
################################################################################

# Indicador de carencia por acceso a los servicios de salud
salud['ic_asalud'] = np.NAN
    # Acceso directo
salud.loc[((salud['sa_dir'] == 1)), 'ic_asalud'] = 0 
    # Parentesco directo: jefatura
salud.loc[((salud['par'] == 1) & (salud['cony_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
salud.loc[((salud['par'] == 1) & (salud['pea'] == 0) & (salud['hijo_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
    # Parentesco directo: cónyuge
salud.loc[((salud['par'] == 2) & (salud['jef_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
salud.loc[((salud['par'] == 2) & (salud['pea'] == 0) & (salud['hijo_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
    # Parentesco directo: descendientes
salud.loc[((salud['par'] == 3) & (salud['edad'] < 16) & (salud['jef_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
salud.loc[((salud['par'] == 3) & (salud['edad'] < 16) & (salud['cony_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
salud.loc[((salud['par'] == 3) & (salud['edad'].between(16, 25)) & (salud['inas_esc'] == 0) & (salud['jef_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
salud.loc[((salud['par'] == 3) & (salud['edad'].between(16, 25)) & (salud['inas_esc'] == 0) & (salud['cony_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
    # Parentesco directo: ascendientes
salud.loc[((salud['par'] == 4) & (salud['pea'] == 0) & (salud['jef_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
salud.loc[((salud['par'] == 5) & (salud['pea'] == 0) & (salud['cony_sa'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
    # Otros núcleos familiares
salud.loc[((salud['s_salud'] == 1)), 'ic_asalud'] = 0 # No presenta carencia
    # Acceso reportado
salud.loc[((salud['pop_insabi'] == 1) | ((salud['pop_insabi'] == 2) & (salud['atemed'] == 1) & 
                                         ((salud['inst_1'] == 1) | (salud['inst_2'] == 2) | (salud['inst_3'] == 3) | 
                                         (salud['inst_4'] == 4) | (salud['inst_5'] == 5) | (salud['inst_6'] == 6))) | 
           (salud['segvol_2'] == 2)), 'ic_asalud'] = 0 # No presenta carencia
salud.loc[(salud['ic_asalud'].isna()), 'ic_asalud'] = 1 # Presenta carencia

# Población con presencia de discapacidad, sea física o mental
salud['discap'] = np.NAN
salud.loc[((salud['disc_camin'] == '3') | (salud['disc_camin'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_ver'] == '3') | (salud['disc_ver'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_brazo'] == '3') | (salud['disc_brazo'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_apren'] == '3') | (salud['disc_apren'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_oir'] == '3') | (salud['disc_oir'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_vest'] == '3') | (salud['disc_vest'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_habla'] == '3') | (salud['disc_habla'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_acti'] == '3') | (salud['disc_acti'] == '4')), 'discap'] = 0 # Sin presencia de discapacidad
salud.loc[((salud['disc_camin'] == '&') | (salud['disc_ver'] == '&') |
          (salud['disc_brazo'] == '&') | (salud['disc_apren'] == '&') |
          (salud['disc_oir'] == '&') | (salud['disc_vest'] == '&') &
          (salud['disc_habla'] == '&') | (salud['disc_acti'] == '&')), 'discap'] = np.NAN # Sin presencia de discapacidad
salud.loc[((salud['disc_camin'] == '1') | (salud['disc_camin'] == '2')), 'discap'] = 1 # Con presencia de discapacidad
salud.loc[((salud['disc_ver'] == '1') | (salud['disc_ver'] == '2')), 'discap'] = 1 # Con presencia de discapacidad
salud.loc[((salud['disc_brazo'] == '1') | (salud['disc_brazo'] == '2')), 'discap'] = 1 # Con presencia de discapacidad
salud.loc[((salud['disc_apren'] == '1') | (salud['disc_apren'] == '2')), 'discap'] = 1 # Con presencia de discapacidad
salud.loc[((salud['disc_oir'] == '1') | (salud['disc_oir'] == '2')), 'discap'] = 1 # Con presencia de discapacidad
salud.loc[((salud['disc_vest'] == '1') | (salud['disc_vest'] == '2')), 'discap'] = 1 # Con presencia de discapacidad
salud.loc[((salud['disc_habla'] == '1') | (salud['disc_habla'] == '2')), 'discap'] = 1 # Con presencia de discapacidad
salud.loc[((salud['disc_acti'] == '1') | (salud['disc_acti'] == '2')), 'discap'] = 1 # Con presencia de discapacidad

salud = salud[['folioviv', 'foliohog', 'numren', 'sexo', 'pop_insabi', 'atemed', 'inst_1', 'inst_2', 'inst_3', 'inst_4', 'inst_5', 'inst_6', 
               'inscr_1', 'inscr_2', 'inscr_3', 'inscr_4', 'inscr_5', 'inscr_6', 'inscr_7', 'inscr_8', 'segvol_1', 'segvol_2', 'segvol_3', 
               'segvol_4', 'segvol_5', 'segvol_6', 'segvol_7', 'sa_dir', 'jef_sa', 'cony_sa', 'hijo_sa', 'ic_asalud', 'discap']]

salud.to_csv('Bases/ic_asalud22.csv', index=False)
del ocupados

################################################################################
#  Pararte III Indicadores de carencias sociales:
#  INDICADOR DE CARENCIA POR ACCESO A LA SEGURIDAD SOCIAL 
################################################################################

# Prestaciones laborales
trab = pd.read_csv('Bases de datos/trabajos.csv', low_memory=False)
prestaciones22 = trab.copy()

#Convirtiendo variables string a numericas
prestaciones22[['subor', 'indep', 'tiene_suel', 'pago', 'pres_8', 'id_trabajo']
     ]=prestaciones22[['subor', 'indep', 'tiene_suel', 'pago', 'pres_8', 'id_trabajo']].apply(pd.to_numeric, errors='coerce')

# Tipo de trabajador: identifica la población subordinada e independiente
prestaciones22['tipo_trab'] = np.NAN
    # Subordinados
prestaciones22.loc[(prestaciones22['subor'] == 1), 'tipo_trab'] = 1
    # Independientes que reciben un pago
prestaciones22.loc[((prestaciones22['subor'] == 2) & (prestaciones22['indep'] == 1) & (prestaciones22['tiene_suel'] == 1)), 'tipo_trab'] = 2
prestaciones22.loc[((prestaciones22['subor'] == 2) & (prestaciones22['indep'] == 2) & (prestaciones22['pago'] == 1)), 'tipo_trab'] = 2
    # Independientes que no reciben un pago
prestaciones22.loc[((prestaciones22['subor'] == 2) & (prestaciones22['indep'] == 1) & (prestaciones22['tiene_suel'] == 2)), 'tipo_trab'] = 3
prestaciones22.loc[((prestaciones22['subor'] == 2) & (prestaciones22['indep'] == 2) & ((prestaciones22['pago'] == 2) | (prestaciones22['pago'] == 3))), 'tipo_trab'] = 3
 
# Ahorro para el retiro o pensión para la vejez (SAR, Afore)
prestaciones22['aforlab'] = np.NAN
prestaciones22.loc[(prestaciones22['pres_8'].isna()), 'aforlab'] = 0 
prestaciones22.loc[(prestaciones22['pres_8'] == 8), 'aforlab'] = 1 

# Ocupación principal o secundaria
prestaciones22['ocupa'] = np.NAN
prestaciones22.loc[(prestaciones22['id_trabajo'] == 1), 'ocupa'] = 1 
prestaciones22.loc[(prestaciones22['id_trabajo'] == 2), 'ocupa'] = 1 

# Distinción de prestaciones en trabajo principal y secundario
prestaciones22 = prestaciones22[['folioviv', 'foliohog', 'numren', 'id_trabajo', 'tipo_trab', 'aforlab', 'ocupa']]

prestaciones22 = pd.pivot_table(prestaciones22, index=['folioviv', 'foliohog', 'numren'], columns='id_trabajo', 
                        values=['tipo_trab', 'aforlab', 'ocupa'], aggfunc=np.sum, fill_value=0)
prestaciones22.columns = [f'{i}{j}' for i, j in prestaciones22.columns]
prestaciones22 = prestaciones22.reset_index()
    # Identificación de la población trabajadora (toda 
    # la que reporta al menos un empleo en la base de trabajos.csv)
prestaciones22['trab'] = 1
prestaciones22 = prestaciones22[['folioviv', 'foliohog', 'numren', 'trab', 'tipo_trab1', 'tipo_trab2', 'aforlab1', 'aforlab2', 'ocupa1', 'ocupa2']]

prestaciones22.to_csv('Bases/prestaciones22.csv', index=False)

# Ingresos por jubilaciones o pensiones
pens = pd.read_csv('Bases de datos/ingresos.csv', low_memory=False)
pens = pens[((pens['clave'] == 'P032') | (pens['clave'] == 'P033') | (pens['clave'] == 'P104') | (pens['clave'] == 'P045'))]

#Convirtiendo variables string a numericas
pens[['mes_1', 'mes_2', 'mes_3', 'mes_4', 'mes_5', 'mes_6', 'ing_1', 'ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']
     ]=pens[['mes_1', 'mes_2', 'mes_3', 'mes_4', 'mes_5', 'mes_6', 'ing_1', 'ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']].apply(pd.to_numeric, errors='coerce')

# Definición de los deflactores 2022 
dic21 =	0.9475376203	
ene22 =	0.9531433002
feb22 =	0.9610510246	
mar22 =	0.9705661414	
abr22 =	0.9758164180	
may22 =	0.9775368933
jun22 =	0.9857919437	
jul22 =	0.9930938669
ago22 =	1.0000000000
sep22 =	1.0062034038
oct22 =	1.0118979346
nov22 =	1.0177217030
dic22 =	1.0216069077

# Se deflactan los ingresos por jubilaciones, pensiones y programas de adultos 
# mayores de acuerdo con el mes de levantamiento
pens['ing_6'] = np.where(pens['mes_6'].isna(), pens['ing_6'] ,
                np.where(pens['mes_6'] == 2, pens['ing_6'] / feb22,
                np.where(pens['mes_6'] == 3, pens['ing_6'] / mar22,
                np.where(pens['mes_6'] == 4, pens['ing_6'] / abr22,
                pens['ing_6'] / may22))))
pens['ing_5'] = np.where(pens['mes_5'].isna(), pens['ing_5'] ,
                np.where(pens['mes_5'] == 3, pens['ing_5'] / mar22,
                np.where(pens['mes_5'] == 4, pens['ing_5'] / abr22,
                np.where(pens['mes_5'] == 5, pens['ing_5'] / may22,
                pens['ing_5'] / jun22))))
pens['ing_4'] = np.where(pens['mes_4'].isna(), pens['ing_4'] ,
                np.where(pens['mes_4'] == 4, pens['ing_4'] / abr22,
                np.where(pens['mes_4'] == 5, pens['ing_4'] / may22,
                np.where(pens['mes_4'] == 6, pens['ing_4'] / jun22,
                pens['ing_4'] / jul22 ))))
pens['ing_3'] = np.where(pens['mes_3'].isna(), pens['ing_3'] ,
                np.where(pens['mes_3'] == 5, pens['ing_3'] / may22,
                np.where(pens['mes_3'] == 6, pens['ing_3'] / jun22,
                np.where(pens['mes_3'] == 7, pens['ing_3'] / jul22,
                pens['ing_3'] / ago22))))
pens['ing_2'] = np.where(pens['mes_2'].isna(), pens['ing_2'] ,
                np.where(pens['mes_2'] == 6, pens['ing_2'] / jun22,
                np.where(pens['mes_2'] == 7, pens['ing_2'] / jul22,
                np.where(pens['mes_2'] == 8, pens['ing_2'] / ago22,
                pens['ing_2'] / sep22))))
pens['ing_1'] = np.where(pens['mes_1'].isna(), pens['ing_1'] ,
                np.where(pens['mes_1'] == 7, pens['ing_1'] / jul22,
                np.where(pens['mes_1'] == 8, pens['ing_1'] / ago22,
                np.where(pens['mes_1'] == 9, pens['ing_1'] / sep22,
                pens['ing_1'] / oct22 ))))

# Ingreso promedio mensual por programas de adultos mayores
pens['ing_pam'] = np.where((pens['clave'] == 'P104') | (pens['clave'] == 'P045'),
                           np.apply_along_axis(np.mean, 1, pens[['ing_1', 'ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']]),0)
# Ingreso promedio mensual por jubilaciones y pensiones
pens['ing_pens'] = np.where((pens['clave'] == 'P032') | (pens['clave'] == 'P033'),
                            np.apply_along_axis(np.mean, 1, pens[['ing_1', 'ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']]),0)

pens = pens.groupby(['folioviv', 'foliohog', 'numren'])[['ing_pens', 'ing_pam']].sum(numeric_only=True)
pens = pens.reset_index()

pens.to_csv('Bases/pensiones22.csv', index=False)

# Construcción del indicador
segsoc = pobla.copy()

# Población objetivo: no se incluye a huéspedes ni trabajadores domésticos
segsoc = segsoc[~((segsoc['parentesco'] >= 400) & (segsoc['parentesco'] < 500) |
                  (segsoc['parentesco'] >= 700) & (segsoc['parentesco'] < 800))]

# Integración de bases
segsoc = pd.merge(segsoc, prestaciones22, on=['folioviv', 'foliohog', 'numren'], how='left')
segsoc = pd.merge(segsoc, pens, on=['folioviv', 'foliohog', 'numren'], how='left')

#Convirtiendo variables string a numericas
segsoc[['parentesco', 'trab', 'edad', 'act_pnea1', 'act_pnea2','ocupa1', 'atemed', 'trabajo_mp',
       'inst_1', 'inst_2', 'inst_3', 'inst_4', 'inst_5', 'inst_6', 
       'inscr_1', 'inscr_2', 'inscr_3', 'inscr_4', 'inscr_5', 'inscr_6', 'inscr_7', 'asis_esc', 'pop_insabi', 'segvol_1']
      ] = segsoc[['parentesco', 'trab', 'edad', 'act_pnea1', 'act_pnea2','ocupa1', 'atemed', 'trabajo_mp',
                 'inst_1', 'inst_2', 'inst_3', 'inst_4', 'inst_5', 'inst_6', 
                 'inscr_1', 'inscr_2', 'inscr_3', 'inscr_4', 'inscr_5', 'inscr_6', 'inscr_7', 'asis_esc', 'pop_insabi', 'segvol_1']].apply(pd.to_numeric, errors='coerce')

# PEA (personas de 16 años o más)
segsoc['pea'] = np.NAN
segsoc.loc[(segsoc['trab'] == 1) & (segsoc['edad'] >= 16) & 
          (~segsoc['edad'].isna()), 'pea'] = 1 # PEA: ocupada
segsoc.loc[((segsoc['act_pnea1'] == 1) | (segsoc['act_pnea2'] == 1)) & 
          (segsoc['edad'] >= 16) & (~segsoc['edad'].isna()),'pea'] = 2 # PEA: desocupada
segsoc.loc[((segsoc['edad'] >= 16) & (~segsoc['edad'].isna()) &
         (((segsoc['act_pnea1'] != 1) | (segsoc['act_pnea1'].isna())) &
         ((segsoc['act_pnea2'] != 1) | (segsoc['act_pnea2'].isna()))) &
         (((segsoc['act_pnea1'] >= 2) & (segsoc['act_pnea1'] <= 6)) |
         ((segsoc['act_pnea2'] >= 2) & (segsoc['act_pnea2'] <= 6)))),'pea'] = 0 # PNEA

# Acceso directo a la seguridad social
    # Ocupación principal
segsoc['tipo_trab1'] = np.where(segsoc['pea'] == 1, segsoc['tipo_trab1'], segsoc['tipo_trab1']) # Depende de un patrón, jefe o superior 
segsoc['tipo_trab1'] = np.where((segsoc['pea'] == 0) | (segsoc['pea'] == 2), np.NAN, segsoc['tipo_trab1']) # No depende de un jefe y recibe o tiene asignado un sueldo
segsoc['tipo_trab1'] = np.where(segsoc['pea'].isna(), np.NAN, segsoc['tipo_trab1']) # No depende de un jefe y no recibe o no tiene asignado un sueldo
    # Ocupación secundaria
segsoc['tipo_trab2'] = np.where(segsoc['pea'] == 1, segsoc['tipo_trab2'], segsoc['tipo_trab2']) # Depende de un patrón, jefe o superior
segsoc['tipo_trab2'] = np.where((segsoc['pea'] == 0) | (segsoc['pea'] == 2), np.NAN, segsoc['tipo_trab2']) # No depende de un jefe y recibe o tiene asignado un sueldo
segsoc['tipo_trab2'] = np.where(segsoc['pea'].isna(), np.NAN, segsoc['tipo_trab2']) # No depende de un jefe y no recibe o no tiene asignado un sueldo
    # Jubilados y pensionados
segsoc['jub'] = np.NAN
segsoc.loc[((segsoc['trabajo_mp'] == 2) & ((segsoc['act_pnea1'] == 2) | (segsoc['act_pnea2'] == 2))), 'jub'] = 1 # Población pensionada o jubilada
segsoc.loc[((segsoc['ing_pens'] > 0) & (~segsoc['ing_pens'].isna())), 'jub'] = 1 # Población pensionada o jubilada
segsoc.loc[(segsoc['inscr_2'] == 2), 'jub'] = 1 # Población pensionada o jubilada
segsoc.loc[(segsoc['jub'].isna()), 'jub'] = 0 # Población no pensionada o jubilada

# Prestaciones básicas

# Prestaciones laborales (Servicios médicos)
    # Ocupación principal
segsoc['smlab1'] = np.NAN
segsoc.loc[(segsoc['ocupa1'] == 1), 'smlab1'] = 0 # Con servicios médicos
segsoc.loc[((segsoc['ocupa1'] == 1) & (segsoc['atemed'] == 1) & 
            ((segsoc['inst_1'] == 1) | (segsoc['inst_2'] == 2) | (segsoc['inst_3'] == 3) | (segsoc['inst_4'] == 4))
            & (segsoc['inscr_1'] == 1)), 'smlab1'] = 1 # Sin servicios médicos
    # Ocupación secundaria
segsoc['smlab2'] = np.NAN
segsoc.loc[(segsoc['ocupa2'] == 1), 'smlab2'] = 0 # Con servicios médicos
segsoc.loc[((segsoc['ocupa2'] == 1) & (segsoc['atemed'] == 1) & 
            ((segsoc['inst_1'] == 1) | (segsoc['inst_2'] == 2) | (segsoc['inst_3'] == 3) | (segsoc['inst_4'] == 4))
            & (segsoc['inscr_1'] == 1)), 'smlab2'] = 1 # Sin servicios médicos

# Contratación voluntaria: servicios médicos y ahorro para el retiro o pensión para 
# la vejez (SAR, Afore, Haber de retiro)
    # Servicios médicos
segsoc['smcv'] = np.NAN
segsoc.loc[((segsoc['edad'] >= 12) & (~segsoc['edad'].isna())), 'smcv'] = 0 # No cuenta
segsoc.loc[((segsoc['atemed'] == 1) & ((segsoc['inst_1'] == 1) | (segsoc['inst_2'] == 2) | (segsoc['inst_3'] == 3) | (segsoc['inst_4'] == 4)) & 
            (segsoc['inscr_6'] == 6) & ((segsoc['edad'] >= 12) & (~segsoc['edad'].isna()))), 'smcv'] = 1 # Sí cuenta
    # SAR o Afore
segsoc['aforecv'] = np.NAN              
segsoc.loc[((segsoc['segvol_1'].isna()) & ((segsoc['edad'] >= 12) & (~segsoc['edad'].isna()))), 'aforecv'] = 0 # No cuenta    
segsoc.loc[((segsoc['segvol_1'] == 1) & ((segsoc['edad'] >= 12) & (~segsoc['edad'].isna()))), 'aforecv'] = 1 # Sí cuenta 
    # Acceso directo a la seguridad social
segsoc['ss_dir'] = np.NAN
segsoc.loc[(segsoc['ss_dir'].isna()), 'ss_dir'] = 0 # Sin acceso
    # Ocupación principal
segsoc.loc[((segsoc['tipo_trab1'] == 1) & (segsoc['smlab1'] == 1)), 'ss_dir'] = 1 # Con acceso
segsoc.loc[((segsoc['tipo_trab1'] == 2) & ((segsoc['smlab1'] == 1) | (segsoc['smcv'] == 1)) & ((segsoc['aforlab1'] == 1) | (segsoc['aforecv'] == 1))), 'ss_dir'] = 1 # Con acceso
segsoc.loc[((segsoc['tipo_trab1'] == 3) & ((segsoc['smlab1'] == 1) | (segsoc['smcv'] == 1)) & (segsoc['aforecv'] == 1)), 'ss_dir'] = 1 # Con acceso
    # Ocupación secundaria
segsoc.loc[((segsoc['tipo_trab2'] == 1) & (segsoc['smlab2'] == 1)), 'ss_dir'] = 1 # Con acceso
segsoc.loc[((segsoc['tipo_trab2'] == 2) & ((segsoc['smlab2'] == 1) | (segsoc['smcv'] == 1)) & ((segsoc['aforlab2'] == 1) | (segsoc['aforecv'] == 1))), 'ss_dir'] = 1 # Con acceso
segsoc.loc[((segsoc['tipo_trab2'] == 3) & ((segsoc['smlab2'] == 1) | (segsoc['smcv'] == 1)) & (segsoc['aforecv'] == 1)), 'ss_dir'] = 1 # Con acceso   
    # Jubilados y pensionados
segsoc.loc[(segsoc['jub'] == 1), 'ss_dir'] = 1 # Con acceso 
    # Núcleos familiares   
segsoc['par'] = np.NAN
segsoc.loc[((segsoc['parentesco'] >= 100) & (segsoc['parentesco'] < 200)), 'par'] = 1 # Jefe o jefa del hogar
segsoc.loc[((segsoc['parentesco'] >= 200) & (segsoc['parentesco'] < 300)), 'par'] = 2 # Cónyuge del  jefe/a
segsoc.loc[((segsoc['parentesco'] >= 300) & (segsoc['parentesco'] < 400)), 'par'] = 3 # Hijo del jefe/a
segsoc.loc[((segsoc['parentesco'] == 601)), 'par'] = 4 # Padre o Madre del jefe/a
segsoc.loc[((segsoc['parentesco'] == 615)), 'par'] = 5 # Suegro del jefe/a
segsoc.loc[(segsoc['par'].isna()), 'par'] = 6 # Sin acceso

# Asimismo, se utilizará la información relativa a la asistencia a la escuela
segsoc['inas_esc'] = np.NAN
segsoc.loc[((segsoc['asis_esc'] == 1)), 'inas_esc'] = 0 # Sí asiste
segsoc.loc[((segsoc['asis_esc'] == 2)), 'inas_esc'] = 1 # No asiste

# En primer lugar se identifican los principales parentescos respecto a la jefatura 
# del hogar y si ese miembro cuenta con acceso directo
segsoc['jef'] = np.NAN
segsoc.loc[((segsoc['par'] == 1) & (segsoc['ss_dir'] == 1)), 'jef'] = 1
segsoc.loc[((((segsoc['inst_2'] == 2) | (segsoc['inst_3'] == 3)) & (segsoc['inscr_6'] == 6)) &
          ((segsoc['inst_1'].isna()) & (segsoc['inst_4'].isna()) & (segsoc['inst_6'].isna())) &
          ((segsoc['inscr_1'].isna()) & (segsoc['inscr_2'].isna()) & (segsoc['inscr_3'].isna()) &
          (segsoc['inscr_4'].isna()) & (segsoc['inscr_5'].isna()) & (segsoc['inscr_7'].isna()))), 'jef'] = np.NAN

segsoc['cony'] = np.NAN
segsoc.loc[((segsoc['par'] == 2) & (segsoc['ss_dir'] == 1)), 'cony'] = 1
segsoc.loc[((((segsoc['inst_2'] == 2) | (segsoc['inst_3'] == 3)) & (segsoc['inscr_6'] == 6)) &
          ((segsoc['inst_1'].isna()) & (segsoc['inst_4'].isna()) & (segsoc['inst_6'].isna())) &
          ((segsoc['inscr_1'].isna()) & (segsoc['inscr_2'].isna()) & (segsoc['inscr_3'].isna()) &
          (segsoc['inscr_4'].isna()) & (segsoc['inscr_5'].isna()) & (segsoc['inscr_7'].isna()))), 'cony'] = np.NAN

segsoc['hijo'] = np.NAN
segsoc.loc[((segsoc['par'] == 3) & (segsoc['ss_dir'] == 1) & (segsoc['jub'] == 1) & ((segsoc['edad'] > 25) & (~segsoc['edad'].isna()))), 'hijo'] = 1
segsoc.loc[((segsoc['par'] == 3) & (segsoc['ss_dir'] == 1) & (segsoc['jub'] == 0)), 'hijo'] = 1
segsoc.loc[((((segsoc['inst_2'] == 2) | (segsoc['inst_3'] == 3)) & (segsoc['inscr_6'] == 6)) &
          ((segsoc['inst_1'].isna()) & (segsoc['inst_4'].isna()) & (segsoc['inst_6'].isna())) &
          ((segsoc['inscr_1'].isna()) & (segsoc['inscr_2'].isna()) & (segsoc['inscr_3'].isna()) &
          (segsoc['inscr_4'].isna()) & (segsoc['inscr_5'].isna()) & (segsoc['inscr_7'].isna()))), 'hijo'] = np.NAN

segsoc = segsoc.groupby(['folioviv', 'foliohog']).apply(lambda x: pd.Series({'jef_ss': x['jef'].sum(skipna=True),
                                                                           'cony_ss': x['cony'].sum(skipna=True),
                                                                           'hijo_ss': x['hijo'].sum(skipna=True)})).reset_index().merge(segsoc, on=['folioviv', 'foliohog'])

segsoc.loc[(segsoc['jef_ss'] > 0), 'jef_ss'] = 1 # Acceso directo a servicios de salud de la jefatura del hogar
segsoc.loc[(segsoc['cony_ss'] > 0), 'cony_ss'] = 1 # Acceso directo a servicios de salud del cónyuge de la jefatura del hogar
segsoc.loc[(segsoc['hijo_ss'] > 0), 'hijo_ss'] = 1 # Acceso directo a servicios de salud de hijos(as) de la jefatura del hogar

# Otros núcleos familiares: se identifica a la población con acceso a la seguridad
# social mediante otros núcleos familiares a través de la afiliación
# o inscripción a servicios de salud por algún familiar dentro o 
# fuera del hogar, muerte del asegurado o por contratación propia

segsoc['s_salud'] = np.NAN
segsoc.loc[((~segsoc['pop_insabi'].isna()) & (~segsoc['atemed'].isna())), 's_salud'] = 0 # Sin acceso
segsoc.loc[((segsoc['atemed'] == 1) & ((segsoc['inst_1'] == 1) | (segsoc['inst_2'] == 2) | (segsoc['inst_3'] == 3) | (segsoc['inst_4'] == 4)) & 
            ((segsoc['inscr_3'] == 3) | (segsoc['inscr_4'] == 4) | (segsoc['inscr_6'] == 6) | (segsoc['inscr_7'] == 7))), 's_salud'] = 1 # Con acceso

# Programas sociales de pensiones para adultos mayores

# Se identifica a las personas de 65 años o más que reciben un programa para adultos mayores
# si el monto recibido es mayor o igual al promedio de la línea de pobreza extrema
# por ingresos rural y urbana

# Valor monetario de las líneas de pobreza extrema por ingresos rural y urbana
lp1_urb = 2086.21
lp1_rur = 1600.18
lp_pam = (lp1_urb + lp1_rur)/2

segsoc['pam'] = np.NAN
segsoc.loc[((segsoc['edad'] >= 65) & (~segsoc['edad'].isna())), 'pam'] = 0 # No recibe
segsoc.loc[((segsoc['edad'] >= 65) & (~segsoc['edad'].isna()) & (segsoc['ing_pam'] >= lp_pam) & (~segsoc['ing_pam'].isna())), 'pam'] = 1 # Recibe

################################################################################
# Indicador de carencia por acceso a la seguridad social
#
# Se encuentra en situación de carencia por acceso a la seguridad social
# a la población que:
#  1. No disponga de acceso directo a la seguridad social.
#  2. No cuente con parentesco directo con alguna persona dentro del hogar
#     que tenga acceso directo.
#  3. No recibe servicios médicos por parte de algún familiar dentro o
#     fuera del hogar, por muerte del asegurado o por contratación propia.
#  4. No recibe ingreso por parte de un programa de adultos mayores donde el
#     monto sea mayor o igual al valor promedio de la canasta alimentaria 
#     rural y urbana.
################################################################################

#Indicador de carencia por acceso a la seguridad social
segsoc['ic_segsoc'] = np.NAN
    # Acceso directo
segsoc.loc[(segsoc['ss_dir'] == 1), 'ic_segsoc'] = 0 # No presenta carencia
    # Parentesco directo: jefatura
segsoc.loc[((segsoc['par'] == 1) & (segsoc['cony_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
segsoc.loc[((segsoc['par'] == 1) & (segsoc['pea'] == 0) & (segsoc['hijo_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
    # Parentesco directo: cónyuge
segsoc.loc[((segsoc['par'] == 2) & (segsoc['jef_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
segsoc.loc[((segsoc['par'] == 2) & (segsoc['pea'] == 0) & (segsoc['hijo_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
    # Parentesco directo: descendientes
segsoc.loc[((segsoc['par'] == 3) & (segsoc['edad'] < 16) & (segsoc['jef_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
segsoc.loc[((segsoc['par'] == 3) & (segsoc['edad'] < 16) & (segsoc['cony_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
segsoc.loc[((segsoc['par'] == 3) & (segsoc['edad'].between(16, 25)) & (segsoc['inas_esc'] == 0) & (segsoc['jef_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
segsoc.loc[((segsoc['par'] == 3) & (segsoc['edad'].between(16, 25)) & (segsoc['inas_esc'] == 0) & (segsoc['cony_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
    # Parentesco directo: ascendientes
segsoc.loc[((segsoc['par'] == 4) & (segsoc['pea'] == 0) & (segsoc['jef_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
segsoc.loc[((segsoc['par'] == 5) & (segsoc['pea'] == 0) & (segsoc['cony_ss'] == 1)), 'ic_segsoc'] = 0 # No presenta carencia
    # Otros núcleos familiares
segsoc.loc[(segsoc['s_salud'] == 1), 'ic_segsoc'] = 0 # No presenta carencia
    # Programa de adultos mayores
segsoc.loc[(segsoc['pam'] == 1), 'ic_segsoc'] = 0 # No presenta carencia
segsoc.loc[(segsoc['ic_segsoc'].isna()), 'ic_segsoc'] = 1 # Presenta carencia

segsoc = segsoc[['folioviv', 'foliohog', 'numren', 'tipo_trab1', 'tipo_trab2', 'aforlab1', 'aforlab2', 'pea', 'jub', 
'smlab1', 'smlab2', 'smcv', 'aforecv', 'ss_dir', 'par', 'jef_ss', 'cony_ss', 'hijo_ss', 's_salud', 'pam', 'ing_pam', 'ic_segsoc']]

segsoc.to_csv('Bases/ic_segsoc22.csv', index=False)
del dic21, ene22, feb22, mar22, abr22, may22, jun22, jul22, ago22, sep22, oct22, nov22, dic22, lp1_rur, lp1_urb, lp_pam, pens, trab, prestaciones22     

################################################################################
# Parte IV Indicadores de carencias sociales:
# INDICADOR DE CARENCIA POR CALIDAD Y ESPACIOS DE LA VIVIENDA
################################################################################

# Material de construcción de la vivienda
viviendas = pd.read_csv('Bases de datos/viviendas.csv', low_memory=False)
cev = viviendas.copy()

concen = pd.read_csv('Bases de datos/concentradohogar.csv', low_memory=False)
cev = pd.merge(cev, concen, on=['folioviv'], how='left')

#Convirtiendo variables string a numericas
cev[['mat_pisos', 'mat_techos', 'mat_pared', 'tot_resid', 'num_cuarto']
      ] = cev[['mat_pisos', 'mat_techos', 'mat_pared', 'tot_resid', 'num_cuarto']].apply(pd.to_numeric, errors='coerce')

# Indicador de carencia por material de piso de la vivienda
    # Material de los pisos de la vivienda
cev['icv_pisos'] = np.NAN
cev.loc[(cev['mat_pisos'] >= 2), 'icv_pisos'] = 0
cev.loc[(cev['mat_pisos'] == 1), 'icv_pisos'] = 1
# Indicador de carencia por material de techos de la vivienda
    # Material de los techos de la vivienda
cev['icv_techos'] = np.NAN
cev.loc[(cev['mat_techos'] >= 3), 'icv_techos'] = 0
cev.loc[(cev['mat_techos'] <= 2), 'icv_techos'] = 1
# Indicador de carencia por material de muros de la vivienda
    # Material de muros en la vivienda
cev['icv_muros'] = np.NAN
cev.loc[(cev['mat_pared'] >= 6), 'icv_muros'] = 0
cev.loc[(cev['mat_pared'] <= 5), 'icv_muros'] = 1
# Espacios en la vivienda (Hacinamiento)
    # Número de residentes en la vivienda
cev['num_ind'] = cev['tot_resid']
    # Número de cuartos en la vivienda
cev['num_cua'] = cev['num_cuarto']
    # Índice de hacinamiento
cev['cv_hac'] = cev['num_ind']/cev['num_cua']
    # Indicador de carencia por hacinamiento en la vivienda
cev['icv_hac'] = np.NAN
cev.loc[((cev['cv_hac'] > 2.5) & (~cev['cv_hac'].isna())), 'icv_hac'] = 1
cev.loc[(cev['cv_hac'] <= 2.5), 'icv_hac'] = 0
       
# Indicador de carencia por calidad y espacios de la vivienda
################################################################################
# Se considera en situación de carencia por calidad y espacios 
# de la vivienda a las personas que residan en viviendas
# que presenten, al menos, una de las siguientes características:
#  
# 1. El material de los pisos de la vivienda es de tierra
# 2. El material del techo de la vivienda es de lámina de cartón o desechos.
# 3. El material de los muros de la vivienda es de embarro o bajareque, de
#    carrizo, bambú o palma, de lámina de cartón, metálica o asbesto, o
#    material de desecho
# 4. La razón de personas por cuarto (hacinamiento) es mayor que 2.5
################################################################################

cev['ic_cv'] = np.NAN
cev.loc[((cev['icv_pisos'] == 1) | (cev['icv_techos'] == 1) | (cev['icv_muros'] == 1) | (cev['icv_hac'] == 1)), 'ic_cv'] = 1 # Con carencia
cev.loc[((cev['icv_pisos'] == 0) & (cev['icv_techos'] == 0) & (cev['icv_muros'] == 0) & (cev['icv_hac'] == 0)), 'ic_cv'] = 0 # Sin carencia  
cev.loc[((cev['icv_pisos'].isna()) | (cev['icv_techos'].isna()) | (cev['icv_muros'].isna()) | (cev['icv_hac'].isna())), 'ic_cv'] = np.NAN
            
cev = cev[['folioviv', 'foliohog', 'icv_pisos', 'icv_techos', 'icv_muros', 'icv_hac', 'ic_cv']]                  
                  
cev.to_csv('Bases/ic_cev22.csv', index=False)                  
                  
################################################################################
# Parte V Indicadores de Privación Social:
# INDICADOR DE CARENCIA POR ACCESO A LOS SERVICIOS BÁSICOS DE LA VIVIENDA
################################################################################
                  
sbv = pd.merge(concen, viviendas, on=['folioviv'], how='left')                  

#Convirtiendo variables string a numericas
sbv[['procaptar', 'disp_agua', 'drenaje', 'disp_elect', 'combustible', 'estufa_chi']
      ] = sbv[['procaptar', 'disp_agua', 'drenaje', 'disp_elect', 'combustible', 'estufa_chi']].apply(pd.to_numeric, errors='coerce')

# Indicador de carencia por acceso al agua
sbv['isb_agua'] = np.NAN
sbv.loc[((sbv['disp_agua'] >= 3) & (~sbv['disp_agua'].isna())), 'isb_agua'] = 1
sbv.loc[((sbv['procaptar'] == 1) & (sbv['disp_agua'] == 4)), 'isb_agua'] = 0
sbv.loc[((sbv['disp_agua'] <= 2) & (~sbv['disp_agua'].isna())), 'isb_agua'] = 0
# Indicador de carencia por servicio de drenaje
sbv['isb_dren'] = np.NAN
sbv.loc[(sbv['drenaje'] >= 3), 'isb_dren'] = 1
sbv.loc[(sbv['drenaje'] <= 2), 'isb_dren'] = 0
# Indicador de carencia por servicios de electricidad
sbv['isb_luz'] = np.NAN
sbv.loc[(sbv['disp_elect'] >= 5), 'isb_luz'] = 1
sbv.loc[(sbv['disp_elect'] <= 4), 'isb_luz'] = 0
# Indicador de carencia por combustible para cocinar
sbv['combus'] = sbv['combustible']
sbv['estufa'] = sbv['estufa_chi']
sbv['isb_combus'] = np.NAN
sbv.loc[(((sbv['combus'] == 1) | (sbv['combus'] == 2)) & (sbv['estufa'] == 2)), 'isb_combus'] = 1
sbv.loc[(((sbv['combus'] == 1) | (sbv['combus'] == 2)) & (sbv['estufa'] == 1)), 'isb_combus'] = 0
sbv.loc[(sbv['combus'].between(3, 6)), 'isb_combus'] = 0

# Indicador de carencia por acceso a los servicios básicos en la vivienda
################################################################################
# Se considera en situación de carencia por servicios básicos en la vivienda 
# a las personas que residan en viviendas que presenten, al menos, 
# una de las siguientes características:
#  
# 1. El agua se obtiene de un pozo, río, lago, arroyo, pipa, o bien, el agua 
#    entubada la adquieren por acarreo de otra vivienda, o de la llave
#    pública o hidrante.
# 2. No cuentan con servicio de drenaje o el desagüe tiene conexión a
#    una tubería que va a dar a un río, lago, mar, barranca o grieta.
# 3. No disponen de energía eléctrica.
# 4. El combustible que se usa para cocinar o calentar los alimentos es
#    leña o carbón sin chimenea.
################################################################################

sbv['ic_sbv'] = np.NAN
sbv.loc[((sbv['isb_agua'] == 1) | (sbv['isb_dren'] == 1) | (sbv['isb_luz'] == 1) | (sbv['isb_combus'] == 1)), 'ic_sbv'] = 1 # Con carencia
sbv.loc[((sbv['isb_agua'] == 0) & (sbv['isb_dren'] == 0) & (sbv['isb_luz'] == 0) & (sbv['isb_combus'] == 0)), 'ic_sbv'] = 0 # Sin carencia 
sbv.loc[((sbv['isb_agua'].isna()) | (sbv['isb_dren'].isna()) | (sbv['isb_luz'].isna()) | (sbv['isb_combus'].isna())), 'ic_sbv'] = np.NAN

sbv = sbv[['folioviv', 'foliohog', 'isb_agua', 'isb_dren', 'isb_luz', 'isb_combus', 'ic_sbv']]

sbv.to_csv('Bases/ic_sbv22.csv', index=False)                  

################################################################################
# Parte VI Indicadores de Privación Social:
# INDICADOR DE CARENCIA POR ACCESO A LA ALIMENTACIÓN NUTRITIVA Y DE CALIDAD
################################################################################

menores = pobla.copy()

# Población objetivo: no se incluye a huéspedes ni trabajadores domésticos
menores = menores[~((menores['parentesco'] >= 400) & (menores['parentesco'] < 500) |
                  (menores['parentesco'] >= 700) & (menores['parentesco'] < 800))]

# Indicador de hogares con menores de 18 años
menores['men'] = np.NAN
menores.loc[(menores['edad'].between(0, 17)), 'men'] = 1

menores = menores.groupby(['folioviv', 'foliohog'])['men'].sum().dropna().reset_index()

menores['id_men'] = np.NAN
menores.loc[((menores['men'] >= 1) & (~menores['men'].isna())), 'id_men'] = 1
menores.loc[(menores['men'] == 0), 'id_men'] = 0

menores = menores[['folioviv', 'foliohog', 'id_men']]

menores.to_csv('Bases/menores22.csv', index=False)                  

hog = pd.read_csv('Bases de datos/hogares.csv', low_memory=False)
ali = hog.copy()

#Convirtiendo variables string a numericas
ali[['acc_alim2', 'acc_alim4', 'acc_alim5', 'acc_alim6', 'acc_alim7', 'acc_alim8', 'acc_alim11', 'acc_alim12', 'acc_alim13', 'acc_alim14', 'acc_alim15', 'acc_alim16']
      ] = ali[['acc_alim2', 'acc_alim4', 'acc_alim5', 'acc_alim6', 'acc_alim7', 'acc_alim8', 'acc_alim11', 'acc_alim12', 'acc_alim13', 'acc_alim14', 'acc_alim15', 'acc_alim16']].apply(pd.to_numeric, errors='coerce')
                  
# Parte 1. Grado de inseguridad alimentaria  
                
# SEIS PREGUNTAS PARA HOGARES SIN POBLACIÓN MENOR A 18 AÑOS
    # Algún adulto tuvo una alimentación basada en muy poca variedad de alimentos
ali['ia_1ad'] = np.NAN
ali.loc[(ali['acc_alim4'] == 2), 'ia_1ad'] = 0 # No
ali.loc[(ali['acc_alim4'].isna()), 'ia_1ad'] = 0 # No
ali.loc[(ali['acc_alim4'] == 1), 'ia_1ad'] = 1 # Sí
    # Algún adulto dejó de desayunar, comer o cenar
ali['ia_2ad'] = np.NAN
ali.loc[(ali['acc_alim5'] == 2), 'ia_2ad'] = 0 # No
ali.loc[(ali['acc_alim5'].isna()), 'ia_2ad'] = 0 # No
ali.loc[(ali['acc_alim5'] == 1), 'ia_2ad'] = 1 # Sí
    # Algún adulto comió menos de lo que debía comer
ali['ia_3ad'] = np.NAN
ali.loc[(ali['acc_alim6'] == 2), 'ia_3ad'] = 0 # No
ali.loc[(ali['acc_alim6'].isna()), 'ia_3ad'] = 0 # No
ali.loc[(ali['acc_alim6'] == 1), 'ia_3ad'] = 1 # Sí
    # El hogar se quedó sin comida
ali['ia_4ad'] = np.NAN
ali.loc[(ali['acc_alim2'] == 2), 'ia_4ad'] = 0 # No
ali.loc[(ali['acc_alim2'].isna()), 'ia_4ad'] = 0 # No
ali.loc[(ali['acc_alim2'] == 1), 'ia_4ad'] = 1 # Sí
    # Algún adulto sintió hambre pero no comió
ali['ia_5ad'] = np.NAN
ali.loc[(ali['acc_alim7'] == 2), 'ia_5ad'] = 0 # No
ali.loc[(ali['acc_alim7'].isna()), 'ia_5ad'] = 0 # No
ali.loc[(ali['acc_alim7'] == 1), 'ia_5ad'] = 1 # Sí
    # Algún adulto solo comió una vez al día o dejó de comer todo un día
ali['ia_6ad'] = np.NAN
ali.loc[(ali['acc_alim8'] == 2), 'ia_6ad'] = 0 # No
ali.loc[(ali['acc_alim8'].isna()), 'ia_6ad'] = 0 # No
ali.loc[(ali['acc_alim8'] == 1), 'ia_6ad'] = 1 # Sí    

# SEIS PREGUNTAS PARA HOGARES CON POBLACIÓN MENOR A 18 AÑOS
    # Alguien de 0 a 17 años tuvo una alimentación basada en muy poca variedad de alimentos
ali['ia_7men'] = np.NAN
ali.loc[(ali['acc_alim11'] == 2), 'ia_7men'] = 0 # No
ali.loc[(ali['acc_alim11'].isna()), 'ia_7men'] = 0 # No
ali.loc[(ali['acc_alim11'] == 1), 'ia_7men'] = 1 # Sí 
    # Alguien de 0 a 17 años comió menos de lo que debía
ali['ia_8men'] = np.NAN
ali.loc[(ali['acc_alim12'] == 2), 'ia_8men'] = 0 # No
ali.loc[(ali['acc_alim12'].isna()), 'ia_8men'] = 0 # No
ali.loc[(ali['acc_alim12'] == 1), 'ia_8men'] = 1 # Sí 
    # Se tuvo que disminuir la cantidad servida en las comidas a alguien de 0 a 17 años
ali['ia_9men'] = np.NAN
ali.loc[(ali['acc_alim13'] == 2), 'ia_9men'] = 0 # No
ali.loc[(ali['acc_alim13'].isna()), 'ia_9men'] = 0 # No
ali.loc[(ali['acc_alim13'] == 1), 'ia_9men'] = 1 # Sí 
    # Alguien de 0 a 17 años sintió hambre pero no comió
ali['ia_10men'] = np.NAN
ali.loc[(ali['acc_alim14'] == 2), 'ia_10men'] = 0 # No
ali.loc[(ali['acc_alim14'].isna()), 'ia_10men'] = 0 # No
ali.loc[(ali['acc_alim14'] == 1), 'ia_10men'] = 1 # Sí 
    # Alguien de 0 a 17 años se acostó con hambre
ali['ia_11men'] = np.NAN
ali.loc[(ali['acc_alim15'] == 2), 'ia_11men'] = 0 # No
ali.loc[(ali['acc_alim15'].isna()), 'ia_11men'] = 0 # No
ali.loc[(ali['acc_alim15'] == 1), 'ia_11men'] = 1 # Sí 
    # Alguien de 0 a 17 años comió una vez al día o dejó de comer todo un día
ali['ia_12men'] = np.NAN
ali.loc[(ali['acc_alim16'] == 2), 'ia_12men'] = 0 # No
ali.loc[(ali['acc_alim16'].isna()), 'ia_12men'] = 0 # No
ali.loc[(ali['acc_alim16'] == 1), 'ia_12men'] = 1 # Sí 

ali = pd.merge(ali, menores, on=['folioviv', 'foliohog'], how='left')

#Convirtiendo variables string a numericas
ali[['id_men', 'ia_1ad', 'ia_2ad', 'ia_3ad', 'ia_4ad', 'ia_5ad', 'ia_6ad', 'ia_7men', 'ia_8men', 'ia_9men', 'ia_10men', 'ia_11men', 'ia_12men',
     'alim17_1', 'alim17_2', 'alim17_3', 'alim17_4', 'alim17_5', 'alim17_6', 'alim17_7', 'alim17_8', 'alim17_9','alim17_10', 'alim17_11', 'alim17_12']
      ] = ali[['id_men', 'ia_1ad', 'ia_2ad', 'ia_3ad', 'ia_4ad', 'ia_5ad', 'ia_6ad', 'ia_7men', 'ia_8men', 'ia_9men', 'ia_10men', 'ia_11men', 'ia_12men',
               'alim17_1', 'alim17_2', 'alim17_3', 'alim17_4', 'alim17_5', 'alim17_6', 'alim17_7', 'alim17_8', 'alim17_9', 'alim17_10', 'alim17_11', 'alim17_12']].apply(pd.to_numeric, errors='coerce')

# Construcción de la escala de inseguridad alimentaria
    # Escala para hogares sin menores de 18 años
ali['tot_iaad'] = np.NAN 
ali.loc[(ali['id_men'] == 0), 'tot_iaad'] = (ali['ia_1ad']) + (ali['ia_2ad']) + (ali['ia_3ad']) + (ali['ia_4ad']) + (ali['ia_5ad']) + (ali['ia_6ad'])
    # Escala para hogares con menores de 18 años
ali['tot_iamen'] = np.NAN 
ali.loc[(ali['id_men'] == 1), 'tot_iamen'] = (ali['ia_1ad']) + (ali['ia_2ad']) + (ali['ia_3ad']) + (ali['ia_4ad']) + (ali['ia_5ad']) + (ali['ia_6ad']) + (ali['ia_7men']) + (ali['ia_8men']) + (ali['ia_9men']) + (ali['ia_10men']) + (ali['ia_11men']) + (ali['ia_12men'])
    # Grado de inseguridad alimentaria
ali['ins_ali'] = np.NAN
    # Seguridad alimentaria 
ali.loc[((ali['tot_iaad'] == 0) | (ali['tot_iamen'] == 0)), 'ins_ali'] = 0
    # Inseguridad alimentaria leve
ali.loc[((ali['tot_iaad'] == 1) | (ali['tot_iaad'] == 2) | (ali['tot_iamen'] == 1) | (ali['tot_iamen'] == 2) | (ali['tot_iamen'] == 3)), 'ins_ali'] = 1
    # Inseguridad alimentaria moderada
ali.loc[((ali['tot_iaad'] == 3) | (ali['tot_iaad'] == 4) | (ali['tot_iamen'] == 4) | (ali['tot_iamen'] == 5) | (ali['tot_iamen'] == 6) | (ali['tot_iamen'] == 7)), 'ins_ali'] = 2
    # Inseguridad alimentaria severa
ali.loc[((ali['tot_iaad'] == 5) | (ali['tot_iaad'] == 6) | (ali['tot_iamen'] >= 8) & (~ali['tot_iamen'].isna())), 'ins_ali'] = 3   

# Se genera el indicador de carencia por acceso a la alimentación que
# considera en situación de carencia a la población en hogares que 
# presenten inseguridad alimentaria moderada o severa

#Indicador de carencia por acceso a la alimentación
ali['ic_ali'] = np.NAN
ali.loc[((ali['ins_ali'] == 2) | (ali['ins_ali'] == 3)), 'ic_ali'] = 1 # Con carencia
ali.loc[((ali['ins_ali'] == 0) | (ali['ins_ali'] == 1)), 'ic_ali'] = 0 # Sin carencia

# Parte 2. Limitación en el consumo de alimentos

# Se considera el número de días que se consumieron cada uno de los 12 grupos 
# de alimentos por el ponderador utilizado por el Programa Mundial de Alimentos (PMA) 
# de las Naciones Unidas:
#
# Grupo 1: (maíz, avena, arroz, sorgo, mijo, pan y otros cereales) y 
#          (yuca, papas, camotes y otros tubérculos)
# Grupo 2: frijoles, chícharos, cacahuates, nueces
# Grupo 3: vegetales y hojas
# Grupo 4: frutas
# Grupo 5: carne de res, cabra, aves, cerdo, huevos y pescado
# Grupo 6: leche, yogur y otros lácteos
# Grupo 7: azúcares y productos azucarados
# Grupo 8: aceites, grasas y mantequilla
# Grupo 9: especias, té, café, sal, polvo de pescado, pequeñas cantidades de 
#          leche para el té

# El ponderador para el Grupo 1 es 2, para el Grupo 2 es 3, para el Grupo 3 y 4 
# es 1, para el Grupo 5 y Grupo 6 es 4, para el Grupo 7 y 8 es 0.5, y para el 
# Grupo 9 es 0
ali['cpond1'] = np.where(ali['alim17_1'] > ali['alim17_2'], ali['alim17_1'], ali['alim17_2']) * 2
ali['cpond3'] = ali['alim17_3'] * 1
ali['cpond4'] = ali['alim17_4'] * 1
ali['cpond5'] = ali[['alim17_5', 'alim17_6', 'alim17_7']].apply(lambda row: max(row), axis=1) * 4
ali['cpond8'] = ali['alim17_8'] * 3
ali['cpond9'] = ali['alim17_9'] * 4
ali['cpond10'] = ali['alim17_10'] * 0.5
ali['cpond11'] = ali['alim17_11'] * 0.5
ali['cpond12'] = ali['alim17_12'] * 0

    # Puntaje total de consumo ponderado de alimentos, indica el número ponderado 
    # de grupos de alimentos que se consumieron en los últimos siete días   
ali['tot_cpond'] = ali['cpond1'] + ali['cpond3'] + ali['cpond4'] + ali['cpond5'] + ali['cpond8'] + ali['cpond9'] + ali['cpond10'] + ali['cpond11'] + ali['cpond12']
    # Se categoriza la dieta consumida en los hogares
    # Dieta consumida en los hogares
ali['dch'] = np.NAN
ali.loc[(ali['tot_cpond'].between(0, 28)), 'dch'] = 1 # Pobre
ali.loc[((ali['tot_cpond'] > 28) & (ali['tot_cpond'] <= 42)), 'dch'] = 2 # Limítrofe
ali.loc[((ali['tot_cpond'] > 42) & (~ali['tot_cpond'].isna())), 'dch'] = 3 # Aceptable
    # Limitación en el consumo de Alimentos
ali['lca'] = np.NAN
ali.loc[((ali['dch'] == 1) | (ali['dch'] == 2)), 'lca'] = 1 # Limitado
ali.loc[(ali['dch'] == 3), 'lca'] = 0 # No limitado

# Indicador de carencia por acceso a la alimentación nutritiva y de calidad
################################################################################
# Se considera en situación de carencia por acceso a la alimentación 
# a la población en hogares que presenten, al menos, una de las 
# siguientes características:
#  
# 1. Grado inseguridad alimentaria moderada o severa
# 2. Limitación en el consumo de alimentos
################################################################################

ali['ic_ali_nc'] = np.NAN
ali.loc[((ali['ic_ali'] == 0) & (ali['lca'] == 0)), 'ic_ali_nc'] = 0 # Sin carencia
ali.loc[((ali['ic_ali'] == 1) | (ali['lca'] == 1) & ((~ali['ic_ali'] .isna()) & (~ali['lca'] .isna()))), 'ic_ali_nc'] = 1 # Con carencia

ali = ali[['folioviv', 'foliohog', 'ia_1ad', 'ia_2ad', 'ia_3ad', 'ia_4ad', 'ia_5ad', 'ia_6ad', 
           'ia_7men', 'ia_8men', 'ia_9men', 'ia_10men', 'ia_11men', 'ia_12men', 'id_men', 
           'tot_iaad', 'tot_iamen', 'ins_ali', 'dch', 'lca', 'ic_ali', 'ic_ali_nc']]

ali.to_csv('Bases/ic_ali22.csv', index=False)  
del hog, menores

################################################################################
# Parte VII
# Bienestar económico (ingresos)
################################################################################

# Para la construcción del ingreso corriente del hogar es necesario utilizar
# información sobre la condición de ocupación y los ingresos de los individuos.
# Se utiliza la información contenida en la base trabajo.csv para 
# identificar a la población ocupada que declara tener como prestación laboral aguinaldo, 
# ya sea por su trabajo principal o secundario, a fin de incorporar los ingresos por este 
# concepto en la medición

# Creación del ingreso monetario deflactado a pesos de agosto del 2022

# Ingresos
trab = pd.read_csv('Bases de datos/trabajos.csv', low_memory=False)
aguinaldo22 = trab.copy()
#Convirtiendo variables string a numericas
aguinaldo22[['numren', 'id_trabajo', 'pres_2']
      ] = aguinaldo22[['numren', 'id_trabajo', 'pres_2']].apply(pd.to_numeric, errors='coerce')

#Generando la base de aguinaldo
aguinaldo22 = pd.pivot_table(aguinaldo22, index=['folioviv', 'foliohog', 'numren'], columns='id_trabajo', 
                          values=['pres_2'], aggfunc=np.sum, fill_value=0)
aguinaldo22.columns = [f'{i}{j}' for i, j in aguinaldo22.columns]
aguinaldo22 = aguinaldo22.reset_index()

aguinaldo22['trab'] = 1 # Población con al menos un empleo 

aguinaldo22['aguinaldo1']=np.where(aguinaldo22['pres_21']==2,1,0) # Aguinaldo trabajo principal
aguinaldo22['aguinaldo2']=np.where(aguinaldo22['pres_22']==2,1,0) # Aguinaldo trabajo secundario

aguinaldo22 = aguinaldo22[['folioviv', 'foliohog', 'numren', 'aguinaldo1', 'aguinaldo2', 'trab']]

aguinaldo22.to_csv('Bases/aguinaldo22.csv', index=False)  
del trab

# Ahora se incorpora a la base de ingresos

ing = pd.read_csv('Bases de datos/ingresos.csv', low_memory=False)

ingreso_deflactado22 = pd.merge(ing, aguinaldo22, on=['folioviv', 'foliohog', 'numren'], how='outer') 

ingreso_deflactado22 = ingreso_deflactado22[~(((ingreso_deflactado22['clave'] == 'P009') & (ingreso_deflactado22['aguinaldo1'] != 1)) |
                                              ((ingreso_deflactado22['clave'] == 'P016') & (ingreso_deflactado22['aguinaldo2'] != 1)))]

# Una vez realizado lo anterior, se procede a deflactar el ingreso recibido
# por los hogares a precios de agosto de 2022. Para ello, se utilizan las 
# variables meses, las cuales toman los valores 2 a 10 e indican el mes en
# que se recibió el ingreso respectivo

# Definición de los deflactores 2022 
dic21 =	0.9475376203	
ene22 =	0.9531433002
feb22 =	0.9610510246	
mar22 =	0.9705661414	
abr22 =	0.9758164180	
may22 =	0.9775368933
jun22 =	0.9857919437	
jul22 =	0.9930938669
ago22 =	1.0000000000
sep22 =	1.0062034038
oct22 =	1.0118979346
nov22 =	1.0177217030
dic22 =	1.0216069077

# Se deflactan los ingresos por jubilaciones, pensiones y programas de adultos 
# mayores de acuerdo con el mes de levantamiento

#Convirtiendo variables string a numericas
ingreso_deflactado22[['mes_1', 'mes_2', 'mes_3', 'mes_4', 'mes_5', 'mes_6', 'ing_1', 'ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']
     ]=ingreso_deflactado22[['mes_1', 'mes_2', 'mes_3', 'mes_4', 'mes_5', 'mes_6', 'ing_1', 'ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']].apply(pd.to_numeric, errors='coerce')

ingreso_deflactado22['ing_6'] = np.where(ingreso_deflactado22['mes_6'].isna(), ingreso_deflactado22['ing_6'] ,
                np.where(ingreso_deflactado22['mes_6'] == 2, ingreso_deflactado22['ing_6'] / feb22,
                np.where(ingreso_deflactado22['mes_6'] == 3, ingreso_deflactado22['ing_6'] / mar22,
                np.where(ingreso_deflactado22['mes_6'] == 4, ingreso_deflactado22['ing_6'] / abr22,
                ingreso_deflactado22['ing_6'] / may22))))
ingreso_deflactado22['ing_5'] = np.where(ingreso_deflactado22['mes_5'].isna(), ingreso_deflactado22['ing_5'] ,
                np.where(ingreso_deflactado22['mes_5'] == 3, ingreso_deflactado22['ing_5'] / mar22,
                np.where(ingreso_deflactado22['mes_5'] == 4, ingreso_deflactado22['ing_5'] / abr22,
                np.where(ingreso_deflactado22['mes_5'] == 5, ingreso_deflactado22['ing_5'] / may22,
                ingreso_deflactado22['ing_5'] / jun22))))
ingreso_deflactado22['ing_4'] = np.where(ingreso_deflactado22['mes_4'].isna(), ingreso_deflactado22['ing_4'] ,
                np.where(ingreso_deflactado22['mes_4'] == 4, ingreso_deflactado22['ing_4'] / abr22,
                np.where(ingreso_deflactado22['mes_4'] == 5, ingreso_deflactado22['ing_4'] / may22,
                np.where(ingreso_deflactado22['mes_4'] == 6, ingreso_deflactado22['ing_4'] / jun22,
                ingreso_deflactado22['ing_4'] / jul22))))
ingreso_deflactado22['ing_3'] = np.where(ingreso_deflactado22['mes_3'].isna(), ingreso_deflactado22['ing_3'] ,
                np.where(ingreso_deflactado22['mes_3'] == 5, ingreso_deflactado22['ing_3'] / may22,
                np.where(ingreso_deflactado22['mes_3'] == 6, ingreso_deflactado22['ing_3'] / jun22,
                np.where(ingreso_deflactado22['mes_3'] == 7, ingreso_deflactado22['ing_3'] / jul22,
                ingreso_deflactado22['ing_3'] / ago22))))
ingreso_deflactado22['ing_2'] = np.where(ingreso_deflactado22['mes_2'].isna(), ingreso_deflactado22['ing_2'] ,
                np.where(ingreso_deflactado22['mes_2'] == 6, ingreso_deflactado22['ing_2'] / jun22,
                np.where(ingreso_deflactado22['mes_2'] == 7, ingreso_deflactado22['ing_2'] / jul22,
                np.where(ingreso_deflactado22['mes_2'] == 8, ingreso_deflactado22['ing_2'] / ago22,
                ingreso_deflactado22['ing_2'] / sep22))))
ingreso_deflactado22['ing_1'] = np.where(ingreso_deflactado22['mes_1'].isna(), ingreso_deflactado22['ing_1'] ,
                np.where(ingreso_deflactado22['mes_1'] == 7, ingreso_deflactado22['ing_1'] / jul22,
                np.where(ingreso_deflactado22['mes_1'] == 8, ingreso_deflactado22['ing_1'] / ago22,
                np.where(ingreso_deflactado22['mes_1'] == 9, ingreso_deflactado22['ing_1'] / sep22,
                ingreso_deflactado22['ing_1'] / oct22))))

# Se deflactan las claves P008 y P015 (Reparto de utilidades) y P009 y P016 (aguinaldo)
# con los deflactores de mayo a agosto 2022 y de diciembre de 2021 a agosto 2022, 
# respectivamente, y se obtiene el promedio mensual

ingreso_deflactado22.loc[ingreso_deflactado22['clave'].isin(['P008', 'P015']), 'ing_1'] = ingreso_deflactado22['ing_1'] / may22 / 12
ingreso_deflactado22.loc[ingreso_deflactado22['clave'].isin(['P009', 'P016']), 'ing_1'] = ingreso_deflactado22['ing_1'] / dic21 / 12

index = ['P008', 'P009', 'P015', 'P016']
cols = ['ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']
for col in cols:
    ingreso_deflactado22.loc[ingreso_deflactado22['clave'].isin(index) & ([col] == 0), col] = None
    
# Una vez realizada la deflactación, se procede a obtener el ingreso mensual 
# promedio en los últimos seis meses, para cada persona y clave de ingreso
ingreso_deflactado22['ing_mens'] = ingreso_deflactado22[['ing_1', 'ing_2', 'ing_3', 'ing_4', 'ing_5', 'ing_6']].mean(axis=1, skipna=True)

# Para obtener el ingreso corriente monetario, se seleccionan las claves de ingreso correspondientes
ingreso_deflactado22.loc[((ingreso_deflactado22['clave'].between('P001', 'P009')) | 
         (ingreso_deflactado22['clave'].between('P011', 'P016')) | 
         (ingreso_deflactado22['clave'].between('P018', 'P048')) | 
         (ingreso_deflactado22['clave'].between('P067', 'P081')) | 
         (ingreso_deflactado22['clave'].between('P101', 'P108'))), 'ing_mon'] = ingreso_deflactado22['ing_mens']

# Para obtener el ingreso laboral, se seleccionan las claves de ingreso correspondientes
ingreso_deflactado22.loc[((ingreso_deflactado22['clave'].between('P001', 'P009')) | 
         (ingreso_deflactado22['clave'].between('P011', 'P016')) | 
         (ingreso_deflactado22['clave'].between('P018', 'P022')) | 
         (ingreso_deflactado22['clave'].between('P067', 'P081'))), 'ing_lab'] = ingreso_deflactado22['ing_mens']

# Para obtener el ingreso por rentas, se seleccionan las claves de ingreso correspondientes
ingreso_deflactado22.loc[ingreso_deflactado22['clave'].between('P023', 'P031'), 'ing_ren'] = ingreso_deflactado22['ing_mens']

# Para obtener el ingreso por transferencias, se seleccionan las claves de ingreso correspondientes
ingreso_deflactado22.loc[((ingreso_deflactado22['clave'].between('P032', 'P048')) | 
         (ingreso_deflactado22['clave'].between('P101', 'P108'))), 'ing_tra'] = ingreso_deflactado22['ing_mens']

# Se estima el total de ingresos de cada  hogar
ingreso_deflactado22 = ingreso_deflactado22.groupby(['folioviv', 'foliohog'])[['ing_mon', 'ing_lab', 'ing_ren', 'ing_tra']].sum(numeric_only=True)
ingreso_deflactado22 = ingreso_deflactado22.reset_index()

ingreso_deflactado22.to_csv('Bases/ingreso_deflactado22.csv', index=False)  
del dic21, ene22, feb22, mar22, abr22, may22, jun22, jul22, ago22, sep22, oct22, nov22, dic22, index, cols, col, ing     

################################################################################
#
#          Creación del ingreso no monetario deflactado a pesos de 
#                                 agosto del 2022
#
################################################################################

#No Monetario
ghog = pd.read_csv('Bases de datos/gastoshogar.csv', low_memory=False).astype(str)
ghog['base'] = 1
gper = pd.read_csv('Bases de datos/gastospersona.csv', low_memory=False).astype(str)
nomon = pd.concat([ghog, gper], ignore_index=True)
nomon.loc[nomon['base'].isna(), 'base'] = 2

nomon.loc[nomon['base'] == 2, 'frecuencia'] = nomon['frec_rem']

# En el caso de la información de gasto no monetario, para deflactar se utiliza 
# la decena de levantamiento de la encuesta, la cual se encuentra en la octava 
# posición del folio de la vivienda. En primer lugar se obtiene una variable que 
# identifique la decena de levantamiento
nomon['decena'] = nomon['folioviv'].astype(str).str.zfill(10).str[7]

# Definición de los deflactores
d11w07 = 0.9869825057
d11w08 = 1.0000000000
d11w09 = 1.0130754464
d11w10 = 1.0178275200
d11w11 = 1.0207468579

# Rubro 1.2 semanal, Bebidas alcohólicas y tabaco		
d12w07 = 0.9923340135
d12w08 = 1.0000000000
d12w09 = 1.0035071112
d12w10 = 1.0111808568
d12w11 = 1.0131982216

# Rubro 2 trimestral, Vestido, calzado y accesorios		
d2t05 = 0.9899050815
d2t06 = 0.9941003723
d2t07 = 0.9997465345
d2t08 = 1.0083352270

# Rubro 3 mensual, viviendas		
d3m07 = 0.9998142481
d3m08 = 1.0000000000
d3m09 = 0.9978682753
d3m10 = 1.0031577830
d3m11 = 1.0197073965

# Rubro 4.2 mensual, Accesorios y artículos de limpieza para el hogar		
d42m07 = 0.9894769136
d42m08 = 1.0000000000
d42m09 = 1.0086286240
d42m10 = 1.0182083142
d42m11 = 1.0237613131

# Rubro 4.2 trimestral, Accesorios y artículos de limpieza para el hogar		
d42t05 = 0.9787953163
d42t06 = 0.9897197934
d42t07 = 0.9993685126
d42t08 = 1.0089456461

# Rubro 4.1 semestral, Muebles y aparatos dómesticos		
d41s02 = 1.0003069312
d41s03 = 0.9993861376
d41s04 = 0.9992122603
d41s05 = 0.9991442214

# Rubro 5.1 trimestral, Salud		
d51t05 = 0.9909917367
d51t06 = 0.9954834527
d51t07 = 0.9994564693
d51t08 = 1.0030487384

# Rubro 6.1.1 semanal, Transporte público urbano		
d611w07 = 0.9963207274
d611w08 = 1.0000000000
d611w09 = 1.0034865488
d611w10 = 1.0052385833
d611w11 = 1.0064912880

# Rubro 6 mensual, Transporte		
d6m07 = 0.9987845893
d6m08 = 1.0000000000
d6m09 = 1.0001664946
d6m10 = 1.0057274150
d6m11 = 1.0076837268

# Rubro 6 semestral, Transporte		
d6s02 = 0.9808628306
d6s03 = 0.9879901879
d6s04 = 0.9927380596
d6s05 = 0.9969378864

# Rubro 7 mensual, Educación y esparcimiento		
d7m07 = 0.9961413091
d7m08 = 1.0000000000
d7m09 = 1.0095233900
d7m10 = 1.0144128271
d7m11 = 1.0174522069

# Rubro 2.3 mensual, Accesorios y cuidados del vestido		
d23m07 = 0.9952443607
d23m08 = 1.0000000000
d23m09 = 1.0081869233
d23m10 = 1.0108184343
d23m11 = 1.0072323555

# Rubro 2.3 trimestral,  Accesorios y cuidados del vestido		
d23t05 = 0.9914948875
d23t06 = 0.9956428139
d23t07 = 1.0011437613
d23t08 = 1.0063351192

# INPC semestral		
dINPCs02 = 0.9773093813
dINPCs03 = 0.9838008772
dINPCs04 = 0.9897404209
dINPCs05 = 0.9957540070

#Convirtiendo variables string a numericas
nomon[['gas_nm_tri', 'gasto_nm']
     ]=nomon[['gas_nm_tri', 'gasto_nm']].apply(pd.to_numeric, errors='coerce')

# Una vez definidos los deflactores, se seleccionan los rubros
nomon['gasnomon'] = nomon['gas_nm_tri'] / 3
nomon.loc[nomon['tipo_gasto'] == 'G4', 'esp'] = 1
nomon.loc[nomon['tipo_gasto'].isin(['G5', 'G6']), 'reg'] = 1
nomon = nomon.loc[~nomon['tipo_gasto'].isin(['G2', 'G3', 'G7'])]

# Control para la frecuencia de los regalos recibidos por el hogar
nomon = nomon[~(((nomon['frecuencia'].between('5', '6')) | (nomon['frecuencia'].isna()) | (nomon['frecuencia'] == '0')) & (nomon['base'] == 1) & (nomon['tipo_gasto'] == 'G5'))]

# Control para la frecuencia de los regalos recibidos por persona
nomon = nomon[~(((nomon['frecuencia'] == '9') | (nomon['frecuencia'].isna())) & (nomon['base'] == 2) & (nomon['tipo_gasto'] == 'G5'))]

# Se deflactan los rubros del gasto no monetario según la decena de levantamiento 
nomon.loc[(nomon['clave'].between('A001', 'A222') | nomon['clave'].between('A242', 'A247')), 'ali_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('A223', 'A241')), 'alta_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('H001', 'H122') | (nomon['clave'] == 'H136')), 'veca_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('G001', 'G016') | nomon['clave'].between('R001', 'R004') | (nomon['clave'] == 'R013')), 'viv_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('C001', 'C024')), 'lim_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('I001', 'I026')), 'cris_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('K001', 'K037')), 'ens_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('J001', 'J072')), 'sal_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('B001', 'B007')), 'tpub_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('M001', 'M018') | nomon['clave'].between('F007', 'F014')), 'tfor_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('F001', 'F006') | nomon['clave'].between('R005', 'R008') | nomon['clave'].between('R010', 'R011')), 'com_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('E001', 'E034') | nomon['clave'].between('H134', 'H135') | nomon['clave'].between('L001', 'L029') | 
           nomon['clave'].between('N003', 'N005') | (nomon['clave'] == 'R009')), 'edre_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('E002', 'E003') | nomon['clave'].between('H134', 'H135')), 'edba_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('D001', 'D026') | (nomon['clave'] == 'H132')), 'cuip_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('H123', 'H131') | (nomon['clave'] == 'H133')), 'accp_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('N001', 'N002') | nomon['clave'].between('N006', 'N016') | nomon['clave'].between('T901', 'T915') | 
           (nomon['clave'] == 'R012')), 'otr_nm'] = nomon['gasnomon']
nomon.loc[(nomon['clave'].between('T901', 'T915') | (nomon['clave'] == 'N013')), 'reda_nm'] = nomon['gasnomon']

# Gasto no monetario en Alimentos deflactado (semanal)
nomon['ali_nm'] = np.where(nomon['decena'].isin(['1','2','3']), nomon['ali_nm']/d11w08,
                           np.where(nomon['decena'].isin(['4','5','6']), nomon['ali_nm']/d11w09,
                                   np.where(nomon['decena'].isin(['7','8','9']), nomon['ali_nm']/d11w10,
                                           nomon['ali_nm']/d11w11)))

# Gasto no monetario en Alcohol y tabaco deflactado (semanal)
nomon['alta_nm'] = np.where(nomon['decena'].isin(['1','2','3']), nomon['alta_nm']/d12w08,
                            np.where(nomon['decena'].isin(['4','5','6']), nomon['alta_nm']/d12w09,
                                    np.where(nomon['decena'].isin(['7','8','9']), nomon['alta_nm']/d12w10,
                                            nomon['alta_nm']/d12w11)))

# Gasto no monetario en Vestido y calzado deflactado (trimestral)
nomon['veca_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['veca_nm']/d2t05,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['veca_nm']/d2t06,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['veca_nm']/d2t07,
                                            nomon['veca_nm']/d2t08)))

# Gasto no monetario en viviendas y servicios de conservación deflactado (mensual)
nomon['viv_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['viv_nm']/d3m07,
                           np.where(nomon['decena'].isin(['3','4','5']), nomon['viv_nm']/d3m08,
                                   np.where(nomon['decena'].isin(['6','7','8']), nomon['viv_nm']/d3m09,
                                           nomon['viv_nm']/d3m10)))

# Gasto no monetario en Artículos de limpieza deflactado (mensual)
nomon['lim_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['lim_nm']/d42m07,
                           np.where(nomon['decena'].isin(['3','4','5']), nomon['lim_nm']/d42m08,
                                   np.where(nomon['decena'].isin(['6','7','8']), nomon['lim_nm']/d42m09,
                                           nomon['lim_nm']/d42m10)))

# Gasto no monetario en Cristalería y blancos deflactado (trimestral)
nomon['cris_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['cris_nm']/d42t05,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['cris_nm']/d42t06,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['cris_nm']/d42t07,
                                            nomon['cris_nm']/d42t08)))

# Gasto no monetario en Enseres domésticos y muebles deflactado (semestral)
nomon['ens_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['ens_nm']/d41s02,
                           np.where(nomon['decena'].isin(['3','4','5']), nomon['ens_nm']/d41s03,
                                   np.where(nomon['decena'].isin(['6','7','8']), nomon['ens_nm']/d41s04,
                                           nomon['ens_nm']/d41s05)))

# Gasto no monetario en Salud deflactado (trimestral)
nomon['sal_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['sal_nm']/d51t05,
                           np.where(nomon['decena'].isin(['3','4','5']), nomon['sal_nm']/d51t06,
                                   np.where(nomon['decena'].isin(['6','7','8']), nomon['sal_nm']/d51t07,
                                           nomon['sal_nm']/d51t08)))

# Gasto no monetario en Transporte público deflactado (semanal)
nomon['tpub_nm'] = np.where(nomon['decena'].isin(['1','2','3']), nomon['tpub_nm']/d611w08,
                            np.where(nomon['decena'].isin(['4','5','6']), nomon['tpub_nm']/d611w09,
                                    np.where(nomon['decena'].isin(['7','8','9']), nomon['tpub_nm']/d611w10,
                                            nomon['tpub_nm']/d611w11)))

# Gasto no monetario en Transporte foráneo deflactado (semestral)
nomon['tfor_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['tfor_nm']/d6s02,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['tfor_nm']/d6s03,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['tfor_nm']/d6s04,
                                            nomon['tfor_nm']/d6s05)))

# Gasto no monetario en Comunicaciones deflactado (mensual)
nomon['com_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['com_nm']/d6m07,
                          np.where(nomon['decena'].isin(['3','4','5']), nomon['com_nm']/d6m08,
                                   np.where(nomon['decena'].isin(['6','7','8']), nomon['com_nm']/d6m09,
                                           nomon['com_nm']/d6m10)))

# Gasto no monetario en Educación y recreación deflactado (mensual)
nomon['edre_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['edre_nm']/d7m07,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['edre_nm']/d7m08,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['edre_nm']/d7m09,
                                            nomon['edre_nm']/d7m10)))

# Gasto no monetario en Educación básica deflactado (mensual)
nomon['edba_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['edba_nm']/d7m07,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['edba_nm']/d7m08,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['edba_nm']/d7m09,
                                            nomon['edba_nm']/d7m10)))

# Gasto no monetario en Cuidado personal deflactado (mensual)
nomon['cuip_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['cuip_nm']/d23m07,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['cuip_nm']/d23m08,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['cuip_nm']/d23m09,
                                            nomon['cuip_nm']/d23m10)))

# Gasto no monetario en Accesorios personales deflactado (trimestral)
nomon['accp_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['accp_nm']/d23t05,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['accp_nm']/d23t06,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['accp_nm']/d23t07,
                                            nomon['accp_nm']/d23t08)))

# Gasto no monetario en Otros gastos y transferencias deflactado (semestral)
nomon['otr_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['otr_nm']/dINPCs02,
                           np.where(nomon['decena'].isin(['3','4','5']), nomon['otr_nm']/dINPCs03,
                                   np.where(nomon['decena'].isin(['6','7','8']), nomon['otr_nm']/dINPCs04,
                                           nomon['otr_nm']/dINPCs05)))

# Gasto no monetario en Regalos Otorgados deflactado
nomon['reda_nm'] = np.where(nomon['decena'].isin(['1','2']), nomon['reda_nm']/dINPCs02,
                            np.where(nomon['decena'].isin(['3','4','5']), nomon['reda_nm']/dINPCs03,
                                    np.where(nomon['decena'].isin(['6','7','8']), nomon['reda_nm']/dINPCs04,
                                            nomon['reda_nm']/dINPCs05)))

nomon.to_csv('Bases/ingresonomonetario_def22.csv', index=False) 

del d11w07, d11w08, d11w09, d11w10, d11w11, d12w07, d12w08, d12w09, d12w10, d12w11, d2t05, d2t06, d2t07, d2t08
del d3m07, d3m08, d3m09, d3m10, d3m11, d42m07, d42m08, d42m09, d42m10, d42m11, d42t05, d42t06, d42t07, d42t08 
del d41s02, d41s03, d41s04, d41s05, d51t05, d51t06, d51t07, d51t08, d611w07, d611w08, d611w09, d611w10, d611w11
del d6m07, d6m08, d6m09, d6m10, d6m11, d6s02, d6s03, d6s04, d6s05, d7m07, d7m08, d7m09, d7m10, d7m11 
del d23m07, d23m08, d23m09, d23m10, d23m11, d23t05, d23t06, d23t07, d23t08, dINPCs02, dINPCs03, dINPCs04, dINPCs05

# Construcción de la base de pagos en especie a partir de la base de gasto no monetario
esp = nomon[nomon['esp'] == 1]

esp = esp.groupby(['folioviv', 'foliohog'])[['gasto_nm', 'ali_nm', 'alta_nm', 'veca_nm', 
        'viv_nm', 'lim_nm', 'cris_nm', 'ens_nm', 'sal_nm', 'tpub_nm', 
        'tfor_nm', 'com_nm', 'edre_nm', 'edba_nm', 'cuip_nm', 'accp_nm', 
        'otr_nm', 'reda_nm']].sum(numeric_only=True)
esp = esp.reset_index()

esp.columns = ['folioviv', 'foliohog', 'gasto_nm', 'ali_nme', 'alta_nme', 'veca_nme', 
        'viv_nme', 'lim_nme', 'cris_nme', 'ens_nme', 'sal_nme', 'tpub_nme', 
        'tfor_nme', 'com_nme', 'edre_nme', 'edba_nme', 'cuip_nme', 'accp_nme', 
        'otr_nme', 'reda_nme']

esp.to_csv('bases/esp_def22.csv', index=False)

# Construcción de base de regalos a partir de la base no monetaria
reg = nomon[nomon['reg'] == 1]

reg = reg.groupby(['folioviv', 'foliohog'])[['gasto_nm', 'ali_nm', 'alta_nm', 'veca_nm', 
        'viv_nm', 'lim_nm', 'cris_nm', 'ens_nm', 'sal_nm', 'tpub_nm', 
        'tfor_nm', 'com_nm', 'edre_nm', 'edba_nm', 'cuip_nm', 'accp_nm', 
        'otr_nm', 'reda_nm']].sum(numeric_only=True)
reg = reg.reset_index()

reg.columns = ['folioviv', 'foliohog', 'gasto_nm', 'ali_nmr', 'alta_nmr', 'veca_nmr', 
        'viv_nmr', 'lim_nmr', 'cris_nmr', 'ens_nmr', 'sal_nmr', 'tpub_nmr', 
        'tfor_nmr', 'com_nmr', 'edre_nmr', 'edba_nmr', 'cuip_nmr', 'accp_nmr', 
        'otr_nmr', 'reda_nmr']

reg.to_csv('bases/reg_def22.csv', index=False)

################################################################################
#
#                Construcción del ingreso corriente total
#
################################################################################

ict = concen[['folioviv', 'foliohog', 'tam_loc', 'factor', 'tot_integ', 'est_dis', 'upm', 'ubica_geo']]

# Incorporación de la base de ingreso monetario deflactado
ict = pd.merge(ict, ingreso_deflactado22, on=['folioviv', 'foliohog'], how='left')

# Incorporación de la base de ingreso no monetario deflactado: pago en especie
esp = pd.read_csv('bases/esp_def22.csv', low_memory=False)
ict = pd.merge(ict, esp, on=['folioviv', 'foliohog'], how='left')

# Incorporación de la base de ingreso no monetario deflactado: regalos en especie
reg = pd.read_csv('bases/reg_def22.csv', low_memory=False)
ict = pd.merge(ict, reg, on=['folioviv', 'foliohog'], how='left')

ict.loc[ict['tam_loc']==4, 'rururb'] = 1 # Rural
ict.loc[ict['tam_loc']<=3, 'rururb'] = 0 # Urbano

# Ingreso corriente no monetario pago especie
ict['pago_esp'] = ict[['ali_nme', 'alta_nme', 'veca_nme', 'viv_nme', 'lim_nme', 'cris_nme', 'ens_nme', 'sal_nme', 
                       'tpub_nme', 'tfor_nme', 'com_nme', 'edre_nme', 'cuip_nme', 'accp_nme', 'otr_nme']].sum(axis=1)

# Ingreso corriente no monetario regalos especie
ict['reg_esp'] = ict[['ali_nmr', 'alta_nmr', 'veca_nmr', 'viv_nmr', 'lim_nmr', 'cris_nmr', 'ens_nmr', 'sal_nmr', 
                      'tpub_nmr', 'tfor_nmr', 'com_nmr', 'edre_nmr', 'cuip_nmr', 'accp_nmr', 'otr_nmr']].sum(axis=1)

# Ingreso corriente no monetario
ict['nomon'] = ict[['pago_esp', 'reg_esp']].sum(axis=1)

# Se construye el Ingreso Corriente Total con el ingreso monetario y el ingreso no monetario 
ict['ict'] = ict[['ing_mon', 'nomon']].sum(axis=1)

ict = ict[['folioviv', 'foliohog', 'ubica_geo', 'tam_loc', 'est_dis', 'upm', 'factor', 'tot_integ', 'ing_mon', 'ing_lab', 'ing_ren', 'ing_tra', 
           'ali_nme', 'alta_nme', 'veca_nme', 'viv_nme', 'lim_nme', 'cris_nme', 'ens_nme', 'sal_nme', 'tpub_nme', 'tfor_nme', 'com_nme', 'edre_nme',
           'edba_nme', 'cuip_nme', 'accp_nme', 'otr_nme', 'reda_nme', 'ali_nmr', 'alta_nmr', 'veca_nmr', 'viv_nmr', 'lim_nmr', 'cris_nmr', 'ens_nmr', 
           'sal_nmr', 'tpub_nmr', 'tfor_nmr', 'com_nmr', 'edre_nmr', 'edba_nmr', 'cuip_nmr', 'accp_nmr', 'otr_nmr', 'reda_nmr', 'rururb', 'pago_esp',
           'reg_esp', 'nomon', 'ict']]

ict.to_csv('bases/ingresotot22.csv', index=False)

################################################################################
#
#        Construcción del tamaño de hogar con economías de escala
#                       y escalas de equivalencia
#
################################################################################

tam_hogesc = pobla.copy()

# Población objetivo: no se incluye a huéspedes ni trabajadores domésticos
tam_hogesc = tam_hogesc.loc[~((tam_hogesc['parentesco'] >= 400) & (tam_hogesc['parentesco'] < 500) |
                    (tam_hogesc['parentesco'] >= 700) & (tam_hogesc['parentesco'] < 800))]

# Total de integrantes del hogar
tam_hogesc['ind'] = 1

tam_hogesc['tot_ind'] = tam_hogesc.groupby(['folioviv', 'foliohog'])['ind'].transform('sum')

############################
# Escalas de equivalencia #
############################
tam_hogesc.loc[(tam_hogesc['edad']>=0) & (tam_hogesc['edad']<=5), 'n_05'] = 1
tam_hogesc.loc[(tam_hogesc['edad']<0) | (tam_hogesc['edad']>5), 'n_05'] = 0

tam_hogesc.loc[(tam_hogesc['edad']>=6) & (tam_hogesc['edad']<=12), 'n_6_12'] = 1
tam_hogesc.loc[(tam_hogesc['edad']<6) | (tam_hogesc['edad']>12), 'n_6_12'] = 0

tam_hogesc.loc[(tam_hogesc['edad']>=13) & (tam_hogesc['edad']<=18), 'n_13_18'] = 1
tam_hogesc.loc[(tam_hogesc['edad']<13) | (tam_hogesc['edad']>18), 'n_13_18'] = 0

tam_hogesc.loc[(tam_hogesc['edad']>=19), 'n_19'] = 1
tam_hogesc.loc[(tam_hogesc['edad']<19), 'n_19'] = 0

tam_hogesc.loc[tam_hogesc['n_05']==1, 'tamhogesc'] = tam_hogesc['n_05']*.7031
tam_hogesc.loc[tam_hogesc['n_6_12']==1, 'tamhogesc'] = tam_hogesc['n_6_12']*.7382
tam_hogesc.loc[tam_hogesc['n_13_18']==1, 'tamhogesc'] = tam_hogesc['n_13_18']*.7057
tam_hogesc.loc[tam_hogesc['n_19']==1, 'tamhogesc'] = tam_hogesc['n_19']*.9945
tam_hogesc.loc[tam_hogesc['tot_ind']==1, 'tamhogesc'] = 1

tam_hogesc = tam_hogesc.groupby(['folioviv', 'foliohog'])['tamhogesc'].sum().reset_index()

tam_hogesc.to_csv('bases/tamhogesc22.csv', index=False)

################################################################################
#
#                        Bienestar económico
#
################################################################################

# Incorporación de la información sobre el tamaño del hogar ajustado
p_ing = pd.merge(ict, tam_hogesc, on=['folioviv', 'foliohog'], how='left')

# Información per cápita
p_ing['ictpc'] = p_ing['ict']/p_ing['tamhogesc']

################################################################################
#
#                        Indicadores de Bienestar económico 
#
################################################################################
#
# LP I: Valor de la Canasta alimentaria 
#
# LP II: Valor de la Canasta Alimentaria más el valor de la canasta
# no alimentaria (ver Anexo A del documento metodológico).
#
# En este programa se construyen los indicadores de bienestar por ingresos
# mediante las 2 líneas definidas por CONEVAL , denominándolas:
#  
#  lp1 : Línea de Pobreza Extrema por Ingresos (LPEI)
#  lp2 : Línea de Pobreza por Ingresos (LPI)
#
# Para más información, se sugiere consultar el documento metodológico de Construcción
# de las líneas de pobreza por ingresos. Disponible en:
# https://www.coneval.org.mx/InformesPublicaciones/InformesPublicaciones/Documents/Lineas_pobreza.pdf
################################################################################


#Línea de pobreza extrema por ingresos (LPEI)
# Valor monetario de la canasta alimentaria
lp1_urb = 2086.21
lp1_rur = 1600.18

# Línea de pobreza por ingresos (LPI)
# Valor monetario de la canasta alimentaria más el valor monetario de la canasta no alimentaria
lp2_urb = 4158.35
lp2_rur = 2970.76

# Se identifica a los hogares bajo lp1
p_ing.loc[(p_ing['ictpc']<lp1_urb) & (p_ing['rururb']==0), 'plp_e'] = 1
p_ing.loc[(p_ing['ictpc']>=lp1_urb) & (p_ing['rururb']==0), 'plp_e'] = 0
p_ing.loc[(p_ing['ictpc']<lp1_rur) & (p_ing['rururb']==1), 'plp_e'] = 1
p_ing.loc[(p_ing['ictpc']>=lp1_rur) & (p_ing['rururb']==1), 'plp_e'] = 0

# Se identifica a los hogares bajo lp2
p_ing.loc[(p_ing['ictpc']<lp2_urb) & (p_ing['rururb']==0), 'plp'] = 1
p_ing.loc[(p_ing['ictpc']>=lp2_urb) & (p_ing['rururb']==0), 'plp'] = 0
p_ing.loc[(p_ing['ictpc']<lp2_rur) & (p_ing['rururb']==1), 'plp'] = 1
p_ing.loc[(p_ing['ictpc']>=lp2_rur) & (p_ing['rururb']==1), 'plp'] = 0

p_ing = p_ing[['folioviv', 'foliohog', 'factor', 'tam_loc', 'rururb', 'tamhogesc', 'ict', 'ictpc', 'plp_e', 'plp', 
               'est_dis', 'upm', 'ubica_geo', 'tot_integ', 'ing_mon', 'ing_lab', 'ing_ren', 'ing_tra', 'nomon', 'pago_esp', 'reg_esp']]

p_ing.to_csv('bases/p_ingresos22.csv', index=False)

del aguinaldo22, concen, esp, ghog, gper, ict, ingreso_deflactado22, lp1_rur, lp1_urb, lp2_rur, lp2_urb, nomon , pobla, reg, tam_hogesc, viviendas

################################################################################
#
#                           Parte VIII Pobreza multidimensional
#
################################################################################

############################
# Integración de las bases #
############################
pobreza = pd.merge(rezedu, salud, on=['folioviv', 'foliohog', 'numren'], how='left')
pobreza = pd.merge(pobreza, segsoc, on=['folioviv', 'foliohog', 'numren'], how='left')
pobreza = pd.merge(pobreza, cev, on=['folioviv', 'foliohog'], how='left')
pobreza = pd.merge(pobreza, sbv, on=['folioviv', 'foliohog'], how='left')
pobreza = pd.merge(pobreza, ali, on=['folioviv', 'foliohog'], how='left')
pobreza = pd.merge(pobreza, p_ing, on=['folioviv', 'foliohog'], how='left')

pobreza['ing_mon'].fillna(0, inplace=True)
pobreza['ing_lab'].fillna(0, inplace=True)
pobreza['ing_ren'].fillna(0, inplace=True)
pobreza['ing_tra'].fillna(0, inplace=True)

# Se eliminan posibles duplicados
pobreza = pobreza.drop_duplicates(subset=['folioviv', 'foliohog', 'numren'], keep='first')

pobreza['folioviv'] = pobreza['folioviv'].astype(str).str.zfill(10)
pobreza['ent'] = pobreza['folioviv'].str[:2].astype(int)

entidad = {
    1: 'Aguascalientes',
    2: 'Baja California',
    3: 'Baja California Sur',
    4: 'Campeche',
    5: 'Coahuila',
    6: 'Colima',
    7: 'Chiapas',
    8: 'Chihuahua',
    9: 'Ciudad de México',
    10: 'Durango',
    11: 'Guanajuato',
    12: 'Guerrero',
    13: 'Hidalgo',
    14: 'Jalisco',
    15: 'México',
    16: 'Michoacán',
    17: 'Morelos',
    18: 'Nayarit',
    19: 'Nuevo León',
    20: 'Oaxaca',
    21: 'Puebla',
    22: 'Querétaro',
    23: 'Quintana Roo',
    24: 'San Luis Potosí',
    25: 'Sinaloa',
    26: 'Sonora',
    27: 'Tabasco',
    28: 'Tamaulipas',
    29: 'Tlaxcala',
    30: 'Veracruz',
    31: 'Yucatán',
    32: 'Zacatecas'}

pobreza['entidad'] = pobreza['ent'].map(entidad)

##############################
# Índice de Privación Social #
##############################
pobreza['i_privacion'] = pobreza[['ic_rezedu', 'ic_asalud', 'ic_segsoc', 'ic_cv', 'ic_sbv', 'ic_ali_nc']].sum(axis=1)

pobreza.loc[pobreza['ic_rezedu'].isna() | pobreza['ic_asalud'].isna() | pobreza['ic_segsoc'].isna() | pobreza['ic_cv'].isna() 
            | pobreza['ic_sbv'].isna() | pobreza['ic_ali'].isna(), 'i_privacion'] = np.NAN

##############################
# Pobreza multidimensional   #
##############################
# Pobreza
pobreza.loc[(pobreza['plp'] == 1) & (pobreza['i_privacion'] >= 1) & (~pobreza['i_privacion'].isna()), 'pobreza'] = 1 # Pobre
pobreza.loc[((pobreza['plp'] == 0) | (pobreza['i_privacion'] == 0)) & (~pobreza['plp'].isna()) & (~pobreza['i_privacion'].isna()), 'pobreza'] = 0 # No pobre

# Pobreza extrema
pobreza.loc[(pobreza['plp_e'] == 1) & (pobreza['i_privacion'] >= 3) & (~pobreza['i_privacion'].isna()), 'pobreza_e'] = 1 # Pobre extremo
pobreza.loc[((pobreza['plp_e'] == 0) | (pobreza['i_privacion'] < 3)) & (~pobreza['plp_e'].isna()) & (~pobreza['i_privacion'].isna()), 'pobreza_e'] = 0 # No pobre extremo

# Pobreza moderada
pobreza.loc[(pobreza['pobreza'] == 1) & (pobreza['pobreza_e'] == 0), 'pobreza_m'] = 1 # Pobre moderado
pobreza.loc[(pobreza['pobreza'] == 0) | ((pobreza['pobreza'] == 1) & (pobreza['pobreza_e'] == 1)), 'pobreza_m'] = 0 # No pobre moderado

##############################
#   Población vulnerable     #
##############################
# Vulnerables por carencias
pobreza['vul_car'] = 0  
pobreza.loc[(pobreza['plp'] == 0) & (pobreza['i_privacion'] >= 1) & (~pobreza['i_privacion'].isna()), 'vul_car'] = 1 # Vulnerable
pobreza.loc[pd.isna(pobreza['pobreza']), 'vul_car'] = pd.NA # No vulnerable

# Vulnerables por ingresos
pobreza['vul_ing'] = 0  
pobreza.loc[(pobreza['plp'] == 1) & (pobreza['i_privacion'] == 0), 'vul_ing'] = 1 # Vulnerable
pobreza.loc[pd.isna(pobreza['pobreza']), 'vul_ing'] = pd.NA # No vulnerable

###########################################
#   Población no pobre y no vulnerable    #
###########################################
# Población no pobre y no vulnerable
pobreza['no_pobv'] = 0  
pobreza.loc[(pobreza['plp'] == 0) & (pobreza['i_privacion'] == 0), 'no_pobv'] = 1 # Vulnerable
pobreza.loc[pd.isna(pobreza['pobreza']), 'no_pobv'] = pd.NA # No vulnerable

#########################################
#   Población con carencias sociales    #
#########################################
# Población con al menos una carencia
pobreza['carencias'] = 0
pobreza.loc[(pobreza['i_privacion'] >= 1) & (~pobreza['i_privacion'].isna()), 'carencias'] = 1 # Población con al menos una carencia social
pobreza.loc[pd.isna(pobreza['pobreza']), 'carencias'] = pd.NA # Población sin carencias sociales

# Población con tres o más carencias
pobreza['carencias3'] = 0
pobreza.loc[(pobreza['i_privacion'] >= 3) & (~pobreza['i_privacion'].isna()), 'carencias3'] = 1 # Población con al menos tres carencias sociales
pobreza.loc[pd.isna(pobreza['pobreza']), 'carencias3'] = pd.NA # Población con menos de tres carencias sociales

###################
#   Cuadrantes    #
###################
pobreza['cuadrantes'] = np.NAN
pobreza.loc[(pobreza['plp'] == 1) & (pobreza['i_privacion'] >= 1) & (~pobreza['i_privacion'].isna()), 'cuadrantes'] = 1 # Pobres
pobreza.loc[(pobreza['plp'] == 0) & (pobreza['i_privacion'] >= 1) & (~pobreza['i_privacion'].isna()), 'cuadrantes'] = 2 # Vulnerables por carencias
pobreza.loc[(pobreza['plp'] == 1) & (pobreza['i_privacion'] == 0), 'cuadrantes'] = 3 # Vulnerables por ingresos 
pobreza.loc[(pobreza['plp'] == 0) & (pobreza['i_privacion'] == 0), 'cuadrantes'] = 4 # No pobres y no vulnerables

######################################################
#  Profundidad en el espacio del bienestar económico #
######################################################

#Línea de pobreza extrema por ingresos (LPEI)
# Valor monetario de la canasta alimentaria
lp1_urb = 2086.21
lp1_rur = 1600.18

# Línea de pobreza por ingresos (LPI)
# Valor monetario de la canasta alimentaria más el valor monetario de la canasta no alimentaria
lp2_urb = 4158.35
lp2_rur = 2970.76

# FGT (a=1)
# Distancia normalizada del ingreso respecto a la línea de pobreza por ingresos
pobreza.loc[(pobreza['rururb'] == 1) & (pobreza['plp'] == 1), 'prof1'] = (lp2_rur - pobreza['ictpc']) / lp2_rur
pobreza.loc[(pobreza['rururb'] == 0) & (pobreza['plp'] == 1), 'prof1'] = (lp2_urb - pobreza['ictpc']) / lp2_urb
pobreza.loc[(pobreza['prof1'].isna()) & (pobreza['ictpc'].notna()), 'prof1'] = 0

# Distancia normalizada del ingreso respecto a la línea de pobreza extrema por ingresos
pobreza.loc[(pobreza['rururb'] == 1) & (pobreza['plp_e'] == 1), 'prof_e1'] = (lp1_rur - pobreza['ictpc']) / lp1_rur
pobreza.loc[(pobreza['rururb'] == 0) & (pobreza['plp_e'] == 1), 'prof_e1'] = (lp1_urb - pobreza['ictpc']) / lp1_urb
pobreza.loc[(pobreza['prof_e1'].isna()) & (pobreza['ictpc'].notna()), 'prof_e1'] = 0

#############################################
#   Profundidad de la privación social      #
#############################################
pobreza['profun'] = pobreza['i_privacion']/6

#############################################
#   Intensidad de la privación social       #
#############################################             
# Intensidad de la privación social: pobres
pobreza['int_pob'] = pobreza['profun']*pobreza['pobreza']
# Intensidad de la privación social: pobres extremos
pobreza['int_pobe']= pobreza['profun']*pobreza['pobreza_e']
# Intensidad de la privación social: población vulnerable por carencias
pobreza['int_vulcar']=pobreza['profun']*pobreza['vul_car']
# Intensidad de la privación social: población con carencias sociales
pobreza['int_caren'] = pobreza['profun'] * pobreza['carencias']

pobreza = pobreza[['folioviv', 'foliohog', 'numren', 'est_dis', 'upm', 'factor', 'tam_loc', 'rururb', 'ent', 'ubica_geo', 
                   'edad', 'sexo', 'parentesco', 'ic_rezedu', 'anac_e', 'inas_esc', 'niv_ed', 'ic_asalud', 'ic_segsoc', 'sa_dir', 'ss_dir', 
                   's_salud', 'par', 'jef_ss', 'cony_ss', 'hijo_ss', 'pea', 'jub', 'pam', 'ing_pam', 'ic_cv', 'icv_pisos', 'icv_muros', 'icv_techos',
                   'icv_hac', 'ic_sbv', 'isb_agua', 'isb_dren', 'isb_luz', 'isb_combus', 'ic_ali_nc', 'id_men', 'tot_iaad', 'tot_iamen', 'ins_ali', 
                   'ic_ali', 'lca', 'dch', 'plp_e', 'plp', 'pobreza', 'pobreza_e', 'pobreza_m', 'vul_car', 'vul_ing', 'no_pobv', 'i_privacion', 
                   'carencias', 'carencias3', 'cuadrantes', 'prof1', 'prof_e1', 'profun', 'int_pob', 'int_pobe', 'int_vulcar', 'int_caren', 'tamhogesc', 
                   'ictpc', 'ict', 'ing_mon', 'ing_lab', 'ing_ren', 'ing_tra', 'nomon', 'pago_esp', 'reg_esp', 'hli', 'discap']]

del lp1_urb, lp1_rur, lp2_urb, lp2_rur

pobreza.to_csv('bases/pobreza_22.csv', index=False)

################################################################################
#                             Cuadros resultado
################################################################################

# Tabulados básicos 

#############################################
#      RESULTADOS A NIVEL NACIONAL          #
#############################################

base =pobreza[~np.isnan(pobreza['pobreza'] )]
base_pobreza=pobreza[pobreza['pobreza'] ==1]

nac= [
      ['pobreza',np.average(a=base['pobreza'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['pobreza'] ==1]['pobreza'], 
                           weights=base[base['pobreza'] ==1]['factor'], returned=True)[1]/1000000],     
      ['pobreza_m',np.average(a=base['pobreza_m'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['pobreza_m'] ==1]['pobreza_m'], 
                           weights=base[base['pobreza_m'] ==1]['factor'], returned=True)[1]/1000000], 
    ['pobreza_e',np.average(a=base['pobreza_e'], 
                     weights=pobreza[~np.isnan(pobreza['pobreza_e'])]['factor'])*100 ,
      np.average(a=base[base['pobreza_e'] ==1]['pobreza_e'], 
                           weights=base[base['pobreza_e'] ==1]['factor'], returned=True)[1]/1000000],     
      ['vul_car',np.average(a=base['vul_car'], 
                     weights=pobreza[~np.isnan(pobreza['vul_car'] )]['factor'])*100 ,
      np.average(a=base[base['vul_car'] ==1]['vul_car'], 
                           weights=base[base['vul_car'] ==1]['factor'], returned=True)[1]/1000000],
      ['vul_ing',np.average(a=base['vul_ing'], 
                     weights=pobreza[~np.isnan(pobreza['vul_car'])]['factor'])*100 ,
      np.average(a=base[base['vul_ing'] ==1]['vul_ing'], 
                           weights=base[base['vul_ing'] ==1]['factor'], returned=True)[1]/1000000],      
      ['no_pobv',np.average(a=base['no_pobv'], 
                     weights=pobreza[~np.isnan(pobreza['no_pobv'])]['factor'])*100 ,
      np.average(a=base[base['no_pobv'] ==1]['no_pobv'], 
                           weights=base[base['no_pobv'] ==1]['factor'], returned=True)[1]/1000000], 
      ['carencias',np.average(a=base['carencias'], 
                     weights=pobreza[~np.isnan(pobreza['carencias'])]['factor'])*100 ,
      np.average(a=base[base['carencias'] ==1]['carencias'], 
                           weights=base[base['carencias'] ==1]['factor'], returned=True)[1]/1000000],
      ['carencias3',np.average(a=base['carencias3'], 
                     weights=pobreza[~np.isnan(pobreza['carencias3'])]['factor'])*100 ,
      np.average(a=base[base['carencias3'] ==1]['carencias3'], 
                           weights=base[base['carencias3'] ==1]['factor'], returned=True)[1]/1000000],  
      ['ic_rezedu',np.average(a=base['ic_rezedu'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['ic_rezedu'] ==1]['ic_rezedu'], 
                           weights=base[base['ic_rezedu'] ==1]['factor'], returned=True)[1]/1000000],     
      ['ic_asalud',np.average(a=base['ic_asalud'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['ic_asalud'] ==1]['ic_asalud'], 
                           weights=base[base['ic_asalud'] ==1]['factor'], returned=True)[1]/1000000], 
      ['ic_segsoc',np.average(a=base['ic_segsoc'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['ic_segsoc'] ==1]['ic_segsoc'], 
                           weights=base[base['ic_segsoc'] ==1]['factor'], returned=True)[1]/1000000],       
      ['ic_cv',np.average(a=base['ic_cv'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['ic_cv'] ==1]['ic_cv'], 
                           weights=base[base['ic_cv'] ==1]['factor'], returned=True)[1]/1000000],         
      ['ic_sbv',np.average(a=base['ic_sbv'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['ic_sbv'] ==1]['ic_sbv'], 
                           weights=base[base['ic_sbv'] ==1]['factor'], returned=True)[1]/1000000],            
      ['ic_ali_nc',np.average(a=base['ic_ali_nc'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['ic_ali_nc'] ==1]['ic_ali_nc'], 
                           weights=base[base['ic_ali_nc'] ==1]['factor'], returned=True)[1]/1000000],      
      ['plp_e',np.average(a=base['plp_e'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['plp_e'] ==1]['plp_e'], 
                           weights=base[base['plp_e'] ==1]['factor'], returned=True)[1]/1000000],
      ['plp',np.average(a=base['plp'], 
                     weights=base['factor'])*100 ,
      np.average(a=base[base['plp'] ==1]['plp'], 
                           weights=base[base['plp'] ==1]['factor'], returned=True)[1]/1000000]]

titulos = ['Indicador', 'Porcentaje', 'Millones de personas']

print(tabulate(nac,titulos, tablefmt='grid', floatfmt=('.6f')))

################################################################################
# PORCENTAJE Y NÚMERO DE PERSONAS POR INDICADOR DE POBREZA, ENTIDAD FEDERATIVA #
################################################################################

ids=np.unique(pobreza['ent'])

pob_ent_por =[list(j) for j in  zip([np.average(a=base[base['ent']==i]['pobreza'], 
                      weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['pobreza_m'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['pobreza_e'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['vul_car'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['vul_ing'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids])]

titulos = ['pobreza', 'pobreza_m', 'pobreza_e', 'vul_car', 'vul_ing', 'no_pobv']   

print(tabulate(pob_ent_por, titulos, floatfmt=('.6f')))    

pob_ent_tot =[list(j) for j in  zip([np.average(a=base[base['pobreza'] ==1][base['ent']==i]['pobreza'], 
                      weights=base[base['pobreza'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],         
                       [np.average(a=base[base['pobreza_m'] ==1][base['ent']==i]['pobreza_m'], 
                       weights=base[base['pobreza_m'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['pobreza_e'] ==1][base['ent']==i]['pobreza_e'], 
                       weights=base[base['pobreza_e'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['vul_car'] ==1][base['ent']==i]['vul_car'], 
                       weights=base[base['vul_car'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['vul_ing'] ==1][base['ent']==i]['vul_ing'], 
                       weights=base[base['vul_ing'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids])]

print(tabulate(pob_ent_tot, titulos,floatfmt=('.0f')))    

##########################################################################################
# PORCENTAJE Y NÚMERO DE PERSONAS POR INDICADOR DE CARENCIA SOCIAL, ENTIDAD FEDERATIVA   #
##########################################################################################

ids=np.unique(pobreza['ent'])

care_ent_por =[list(j) for j in  zip([np.average(a=base[base['ent']==i]['ic_rezedu'], 
                      weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['ic_asalud'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['ic_segsoc'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['ic_cv'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['ic_sbv'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['ic_ali_nc'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['carencias'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['carencias3'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['plp_e'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids],
                       [np.average(a=base[base['ent']==i]['plp'], 
                       weights=base[base['ent']==i]['factor'])*100 for i in ids])]

titulos = ['ic_rezedu', 'ic_asalud', 'ic_segsoc', 'ic_cv', 'ic_sbv', 'ic_ali_nc',
           'carencias', 'carencias3', 'plp_e', 'plp']   

print(tabulate(care_ent_por, titulos,floatfmt=('.6f')))    

care_ent_tot =[list(j) for j in  zip([np.average(a=base[base['ic_rezedu'] ==1][base['ent']==i]['ic_rezedu'], 
                      weights=base[base['ic_rezedu'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],           
                       [np.average(a=base[base['ic_asalud'] ==1][base['ent']==i]['ic_asalud'], 
                       weights=base[base['ic_asalud'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['ic_segsoc'] ==1][base['ent']==i]['ic_segsoc'], 
                       weights=base[base['ic_segsoc'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['ic_cv'] ==1][base['ent']==i]['ic_cv'], 
                       weights=base[base['ic_cv'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['ic_sbv'] ==1][base['ent']==i]['ic_sbv'], 
                       weights=base[base['ic_sbv'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['ic_ali_nc'] ==1][base['ent']==i]['ic_ali_nc'], 
                       weights=base[base['ic_ali_nc'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['carencias'] ==1][base['ent']==i]['carencias'], 
                       weights=base[base['carencias'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['carencias3'] ==1][base['ent']==i]['carencias3'], 
                       weights=base[base['carencias3'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['plp_e'] ==1][base['ent']==i]['plp_e'], 
                       weights=base[base['plp_e'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids],
                       [np.average(a=base[base['plp'] ==1][base['ent']==i]['plp'], 
                       weights=base[base['plp'] ==1][base['ent']==i]['factor'],returned=True)[1] for i in ids])]

titulos = ['ic_rezedu', 'ic_asalud', 'ic_segsoc', 'ic_cv', 'ic_sbv', 'ic_ali_nc',
           'carencias', 'carencias3', 'plp_e', 'plp']   

print(tabulate(care_ent_tot, titulos,floatfmt=('.0f')))