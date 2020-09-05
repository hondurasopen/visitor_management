# -*- coding: utf-8 -*-
{
    'name': "Visitor Management",
    "author": "César Alejandro Rodriguez",
    'summary': '', 
    'description': """
        Gestión de visitas medicas.
    """,          
    'version': '1.1',
    'depends': ['base',],
    'data': [
        "views/menus.xml",
        "views/doctor_view.xml",
        "views/especialidad_view.xml",
        "views/visit_view.xml",
        
        #"reports/report_planning.xml",
        #"reports/report_planning_view.xml",
    ],
    'update_xml': [
        "security/groups.xml",   
        "security/ir.model.access.csv"
     ],
    'application': True,
}

