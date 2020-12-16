# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px

from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta

from app import app
from data import NASDAQ_LIST, NASDAQ_DICT
from util import *
from scipy.stats import norm
import math

dashboard_layout =[
            # Main Content
            html.Div([
                # Begin Page Content
                html.Div([
                    # Page Heading
                    html.Div([
                        html.H1("Dashboard",className="h3 mb-0 text-gray-800"),
                    ],className="d-sm-flex align-items-center justify-content-between mb-4"),

                    # Content Row
                    html.Div([

                        # Earnings (Monthly) Card Example
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.Div("Monthly Return",className="text-xs font-weight-bold text-primary text-uppercase mb-1"),
                                            html.Div(className="h5 mb-0 font-weight-bold text-gray-800",id='dashboard-monthly-return'),
                                        ],className="col mr-2"),
                                        html.Div(
                                            html.I(className="fas fa-calendar fa-2x text-gray-300"),className="col-auto"
                                        )
                                    ],className="row no-gutters align-items-center")
                                ],className="card-body")
                            ],className="card border-left-primary shadow h-100 py-2")
                        ],className="col-xl-3 col-md-6 mb-4"),
                        
                        # Pending Requests Card Example
                        html.Div(
                            html.Div(
                                html.Div(
                                    html.Div([
                                        html.Div([
                                            html.Div("Total Profit",className="text-xs font-weight-bold text-warning text-uppercase mb-1"),
                                            html.Div(className="h5 mb-0 font-weight-bold text-gray-800",id='dashboard-total-profit'),
                                        ],className="col mr-2"),
                                        html.Div(
                                            html.I(className="fas fa-dollar-sign fa-2x text-gray-300")
                                        ,className="col-auto")
                                    ],className="row no-gutters align-items-center")
                                ,className="card-body")
                            ,className="card border-left-warning shadow h-100 py-2")
                        ,className="col-xl-3 col-md-6 mb-4"),


                        # Earnings (Monthly) Card Example
                        html.Div(
                            html.Div(
                                html.Div(
                                    html.Div([
                                        html.Div([
                                            html.Div("Realized Profit",className="text-xs font-weight-bold text-success text-uppercase mb-1"),
                                            html.Div(className="h5 mb-0 font-weight-bold text-gray-800",id='dashboard-realized-profit'),
                                        ],className="col mr-2"),
                                        html.Div(
                                            html.I(className="fas fa-dollar-sign fa-2x text-gray-300")
                                        ,className="col-auto")
                                    ],className="row no-gutters align-items-center")
                                ,className="card-body")
                            ,className="card border-left-success shadow h-100 py-2")    
                        ,className="col-xl-3 col-md-6 mb-4"),

                        # Earnings (Monthly) Card Example
                        html.Div(
                            html.Div(
                                html.Div(
                                    html.Div([
                                        html.Div([
                                            html.Div("목표달성률",className="text-xs font-weight-bold text-info text-uppercase mb-1"),
                                            html.Div([
                                                html.Div(
                                                    html.Div("50%",className="h5 mb-0 mr-3 font-weight-bold text-gray-800")
                                                ,className="col-auto"),
                                                html.Div(
                                                    html.Div(
                                                        html.Div(
                                                            className="progress-bar bg-info", role="progressbar",
                                                            style={"width": "50%"}, **{'aria-valuenow':"50", 'aria-valuemin':"0",
                                                            'aria-valuemax':"100"}
                                                        )
                                                    ,className="progress progress-sm mr-2")
                                                ,className="col")
                                            ],className="row no-gutters align-items-center")
                                        ],className="col mr-2"),
                                        html.Div(
                                            html.I(className="fas fa-clipboard-list fa-2x text-gray-300")
                                        ,className="col-auto")
                                    ],className="row no-gutters align-items-center")
                                ,className="card-body")
                            ,className="card border-left-info shadow h-100 py-2")
                        ,className="col-xl-3 col-md-6 mb-4"),

                        
                    ],className="row"),

                    html.Div([
                        # Content Column
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H6("개별 주식 주가",className="m-0 font-weight-bold text-primary")
                                ],className="card-header py-3"),
                                html.Div(dcc.Graph(id="dashboard-stock-graph"), className="card-body"),
                            ],className="card shadow mb-4"),
                        ],className="col-xl-8 col-lg-7"),

                        # Pie Chart 
                        html.Div([
                            html.Div([
                                # Card Header - Dropdown
                                html.Div([
                                    html.H6("주식 투자 비율",className="m-0 font-weight-bold text-primary"),
                                ],className="card-header py-3 d-flex flex-row align-items-center justify-content-between"),
                                # Card Body
                                html.Div(dcc.Graph(id="dashboard-stock-donut"),className="card-body")
                            ],className="card shadow mb-4"),
                        ],className="col-xl-4 col-lg-5"),
                    ],className="row"),

                ],className="container-fluid"),
            ],id="content")]

stock_list_layout = [
                # Begin Page Content
                html.Div([
                    # Page Heading
                    html.H1("주식 매수/매도",className="h3 mb-2 text-gray-800"),
                    html.P(["주식을 사고 판 과정을 입력하세요."],className="mb-4"),

                    # Add Trading
                    html.Div([
                        html.Div(
                            html.H6("주식 거래 내역 추가",className="m-0 font-weight-bold text-primary")
                        ,className="card-header py-3"),
                        html.Div(
                            html.Div([
                                html.Div([
                                    dcc.Dropdown(
                                        options=([{'label':v[2]+" ("+v[1]+")", 'value':v[1]} for i,v in NASDAQ_LIST.iterrows()]),
                                        id="stocklist-dropdown",
                                        placeholder='주식명',
                                        value=None,
                                        searchable=True,
                                        clearable=False,
                                        style={'width':"300px",'color':'#858796','margin-left':'10px'}
                                        ),
                                    dcc.DatePickerSingle(
                                        id='stocklist-datepicker',
                                        min_date_allowed=date(1995, 8, 5),
                                        max_date_allowed=date(2020, 9, 19),
                                        initial_visible_month=date(2017, 8, 5),
                                        placeholder='거래일',
                                        style={'margin-left':'20px'}
                                    ),
                                    dcc.Input(
                                        id='stocklist-tradeamount',
                                        type='number',
                                        placeholder="거래량",
                                        min=1,step=1,
                                        style={'margin-left':'30px'}
                                    ),
                                    dcc.Input(
                                        id='stocklist-tradevalue',
                                        type='number',
                                        placeholder="거래금액",
                                        min=1,step=1,
                                        style={'margin-left':'30px'}
                                    ),
                                    dcc.RadioItems(
                                        id='stocklist-tradetype',
                                        options = [
                                            {'label' : "매수",'value':'buy'},
                                            {'label' : "매도",'value':'sell'},
                                        ],
                                        value='buy',
                                        labelStyle={'display': 'inline-block'}
                                        ,style={'margin-left':'30px'}
                                    ),
                                    html.Button(html.I(className="fas fa-check"),className="btn btn-success btn-circle",id='stocklist-submit',style={'margin-left':'30px'})
                                ],className="row",style={'align-items': 'center','justify-content': 'center'})
                                

                            ],className="dropdown no-arrow mb-4")
                        ,className="card-body")
                    ],className="card mb-4"),

                    # DataTables Example
                    html.Div([
                        html.Div(
                            html.H6("주식 거래 내역",className="m-0 font-weight-bold text-primary")
                        ,className="card-header py-3"),
                        html.Div(
                            html.Div(
                                html.Table([
                                    html.Thead(
                                        html.Tr([
                                            html.Th("No."),
                                            html.Th("주식 명"),
                                            html.Th("거래가격(주당)"),
                                            html.Th("거래량"),
                                            html.Th("거래일"),
                                            html.Th("거래 종류"),
                                            html.Th("남은 주식 수"),
                                        ])
                                    ),
                                    html.Tfoot(
                                        html.Tr([
                                            html.Th("No."),
                                            html.Th("주식 명"),
                                            html.Th("거래가격(주당)"),
                                            html.Th("거래량"),
                                            html.Th("거래일"),
                                            html.Th("거래 종류"),
                                            html.Th("남은 주식 수"),
                                        ]) 
                                    ),
                                    html.Tbody(id='stocklist-tbody')
                                ],className="table table-bordered", id="dataTable",style={'width':"100%", 'cellspacing':"0"})
                            ,className="table-responsive",style={"overflow": "scroll", "height": "400px"})
                        ,className="card-body")
                    ],className="card shadow mb-4"),
                ],className="container-fluid")
]

mv_model_layout = [
                # Begin Page Content
                html.Div([
                    # Page Heading
                    html.H1("MV-model",className="h3 mb-2 text-gray-800"),
                    html.P(["MV model으로 주식의 weight를 계산하세요."],className="mb-4"),
                    

                    # Add Trading
                    html.Div([                    
                        html.Div([
                            html.Div([
                                html.Div(
                                    html.H6("주식 추가",className="m-0 font-weight-bold text-primary")
                                ,className="card-header py-3"),
                                html.Div(
                                    html.Div([
                                        html.Div([
                                            dcc.Dropdown(
                                                options=([{'label':v[2]+" ("+v[1]+")", 'value':v[1]} for i,v in NASDAQ_LIST.iterrows()]),
                                                id="mvmodel-stock-selected",
                                                placeholder='주식명',
                                                value=None,
                                                searchable=True,
                                                clearable=False,
                                                style={'width':"400px",'color':'#858796'}                
                                            ),
                                            dbc.Button(html.I(className="fas fa-check"), className="btn btn-success btn-circle btn-sm ml-1", id = 'mvmodel-addstock',n_clicks=0),
                                            dbc.Button(html.I(className="fas fa-trash"), className="btn btn-danger btn-circle btn-sm ml-1", id = 'mvmodel-delstock',n_clicks=0),
                                            ],className='row',style={'align-items': 'center','justify-content': 'center'}),
                                        html.Hr(),
                                        html.Div(id='mvmodel-stocklist')
                                    ],className="dropdown no-arrow mb-4")
                                ,className="card-body")
                            ],className="card mb-4"),
                        ],className="col-lg-6"),
                        html.Div([
                            html.Div([
                                html.Div(
                                    html.H6("주식 거래 내역 추가",className="m-0 font-weight-bold text-primary")
                                ,className="card-header py-3"),
                                html.Div([
                                    html.Div([
                                        dcc.DatePickerSingle(
                                            id='mvmodel-startdate',
                                            min_date_allowed=date(1995, 8, 5),
                                            max_date_allowed=date(2020, 12, 15),
                                            initial_visible_month=date(2020, 1, 1),
                                            placeholder='평가 시작일',
                                        ),
                                        dcc.DatePickerSingle(
                                            id='mvmodel-enddate',
                                            min_date_allowed=date(1995, 8, 5),
                                            max_date_allowed=date(2020, 12, 15),
                                            initial_visible_month=date(2020, 10, 1),
                                            placeholder='평가종료일',
                                            style={'margin-left':'20px'}
                                        ),
                                        dcc.Input(
                                            id='mvmodel-rettarget',
                                            type='number',
                                            placeholder="수익율 target",
                                            min=0,max=1,
                                            style={'margin-left':'5px'}
                                        ),
                                        dbc.Checklist(
                                            id="mvmodel-noshorting",
                                            options=[
                                                {"label": "No Shorting", "value": 'n-sh'},
                                            ],
                                            labelCheckedStyle={"color": "red"},
                                        )                                
                                    ],className="dropdown no-arrow mb-4"),
                                    html.Hr(),
                                    html.Div([
                                        dcc.RadioItems(
                                            id='mvmodel-constraint',
                                            options = [
                                                {'label' : "None",'value':'none'},
                                                {'label' : "Allocation Restrictions",'value':'alre'},
                                                {'label' : "Turnover",'value':'trov'},
                                                {'label' : 'Transaction Costs', 'value':'trco'},
                                                {'label' : "Cardinality", 'value':'card'},
                                                {'label' : "Cardinality(Lasso)", 'value':'cala'},
                                                {'label' : "Cardinality(Elastic net)", 'value':'cael'},
                                                {'label' : "Risk Factor Constraints", 'value':'rifc'},
                                            ],
                                            value='none',
                                            style={'margin-left':'30px'},
                                            labelStyle={'display': 'block'}
                                        ),
                                    ],className="dropdown no-arrow mb-4"),
                                    html.Hr(),
                                    html.Div(className="dropdown no-arrow mb-4",id='mvmodel-constraints-input'),
                                ],className="card-body")
                            ],className="card mb-4")
                        ],className="col-lg-6"),
                    ],className='row'),
                    html.Hr(),
                    dbc.Button([html.Span(html.I(className="fas fa-arrow-right"),className="icon text-white-50"),html.Span("MV Model 적용하기",className="text")],className="btn btn-secondary btn-icon-split",id='mvmodel-done'),
                    html.Hr(),
                    html.Div(id="mvmodel-result"),
                ],className="container-fluid")
]

backtest_layout = [
                # Begin Page Content
                html.Div([
                    # Page Heading
                    html.H1("BackTest",className="h3 mb-2 text-gray-800"),
                    html.P(["BackTest를 진행하세요."],className="mb-4"),

                    # Add Trading
                    html.Div([                    
                        html.Div([
                            html.Div([
                                html.Div(
                                    html.H6("주식 추가",className="m-0 font-weight-bold text-primary")
                                ,className="card-header py-3"),
                                html.Div(
                                    html.Div([
                                        html.Div([
                                            dbc.Button(id = 'backtest-addstock'),
                                            ],className='row',style={'align-items': 'center','justify-content': 'center'}),
                                        html.Div(id='backtest-stocklist')
                                    ],className="dropdown no-arrow mb-4")
                                ,className="card-body")
                            ],className="card mb-4"),
                        ],className="col-lg-6"),
                        html.Div([
                            html.Div([
                                html.Div(
                                    html.H6("주식 거래 내역 추가",className="m-0 font-weight-bold text-primary")
                                ,className="card-header py-3"),
                                html.Div([
                                    html.Div([
                                        dcc.DatePickerSingle(
                                            id='backtest-startdate',
                                            min_date_allowed=date(1995, 8, 5),
                                            max_date_allowed=date(2020, 12, 15),
                                            initial_visible_month=date(2020, 1, 1),
                                            placeholder='평가 시작일',
                                        ),
                                        dcc.DatePickerSingle(
                                            id='backtest-enddate',
                                            min_date_allowed=date(1995, 8, 5),
                                            max_date_allowed=date(2020, 12, 15),
                                            initial_visible_month=date(2020, 10, 1),
                                            placeholder='평가종료일',
                                            style={'margin-left':'20px'}
                                        ),
                                        dbc.Checklist(
                                            id="backtest-dropna",
                                            options=[
                                                {"label": "모든 행이 0인 열 제외", "value": "dropna"},
                                            ],
                                            labelCheckedStyle={"color": "red"},
                                        ) 
                                    ],className="dropdown no-arrow mb-4"),
                                    html.Div([
                                        dcc.Input(
                                            id='backtest-utinp',
                                            type='number',
                                            placeholder="Test단위",
                                            min=1,step=1,
                                            style={'margin-left':'5px'}
                                        ),
                                        dbc.Button("D", className="btn btn-primary", id ='backtest-utbtn',n_clicks=0),
                                        dcc.Input(
                                            id='backtest-lbinp',
                                            type='number',
                                            placeholder="Lookback",
                                            min=1,step=1,
                                            style={'margin-left':'5px'}
                                        ),
                                        dbc.Button("D", className="btn btn-primary", id ='backtest-lbbtn',n_clicks=0),
                                        dcc.Input(
                                            id='backtest-rbinp',
                                            type='number',
                                            placeholder="Rebalancing",
                                            min=1,step=1,
                                            style={'margin-left':'5px'}
                                        ),
                                        dbc.Button("D", className="btn btn-primary", id ='backtest-rbbtn',n_clicks=0),
                                    ],className="dropdown no-arrow mb-4"),    
                                ],className="card-body")
                            ],className="card mb-4")
                        ],className="col-lg-6"),
                    ],className='row'),
                    html.Hr(),
                    dbc.Button([html.Span(html.I(className="fas fa-arrow-right"),className="icon text-white-50"),html.Span("Backtest 적용하기",className="text")],className="btn btn-secondary btn-icon-split",id='backtest-done'),
                    html.Hr(),
                    html.Div(id="backtest-result"),
                    html.Hr(),
                    html.Div([
                        # Content Column
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H6("수익률차트",className="m-0 font-weight-bold text-primary")
                                ],className="card-header py-3"),
                                html.Div(dcc.Graph(id="backtest-snp-graph"), className="card-body"),
                            ],className="card shadow mb-4"),
                        ],className="col-xl-12 col-lg-7"),
                    ],className="row"), 
                    html.Div(id="backtest-snp")
                ],className="container-fluid")
]

ewma_layout = [html.Div([
    # Page Heading
        html.H1("EWMA",className="h3 mb-2 text-gray-800"),
        html.P(["EWMA Test를 진행하세요."],className="mb-4"),
        # Add Trading
        html.Div([
            html.Div([
                html.Div(
                    html.H6("현 거래주식의 EWMA 예측 결과",className="m-0 font-weight-bold text-primary")
                ,className="card-header py-3"),
                html.Div([            
                    html.Div(
                        html.Div(id='ewma_stocks',className='row')
                    ,className="card-body")
                ],className="card mb-4")
            ],className="col-lg-12"),
        ],className='row'),
        html.Div([
            html.Div([
                html.Div(
                    html.H6("Beta & Return 결과",className="m-0 font-weight-bold text-primary")
                ,className="card-header py-3"),
                html.Div([            
                    html.Div([
                        html.Div(
                            html.H6("Backtest result",className="m-0 font-weight-bold text-primary")
                        ,className="card-header py-3"),
                        html.Div([
                            html.Div(
                                html.Table([
                                    html.Thead(
                                        html.Tr([html.Th(i) for i in ['Num','Symbol','Name',html.Div(['beta |',dbc.Button("▼", className="btn btn-primary", id ='ewma-sortbybeta',n_clicks=0)]),html.Div(['return |',dbc.Button("▼", className="btn btn-primary", id ='ewma-sortbyreturn',n_clicks=0)])]])
                                    ),
                                    html.Tbody(id='ewma-tbodylist'),
                                ],className="table table-bordered", id="dataTable",style={'width':"100%", 'cellspacing':"0"})
                            ,className="table-responsive",style={"height": "850px"}),
                            html.Div([
                                dbc.Button("-", className="btn btn-primary", id ='ewma-page-',n_clicks=0),
                                html.H6('1',id='ewma-page'),
                                dbc.Button("+", className="btn btn-primary", id ='ewma-page+',n_clicks=0)
                            ],className='row')
                        ],className="card-body")
                    ],className="card shadow mb-4"),
                ],className="card mb-4")
            ],className="col-lg-12"),
        ],className='row'),
    ],className="container-fluid")
]

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id='local_stocklist', storage_type='local'),
    dcc.Store(id='session_mvmodel_stocklist', storage_type='session'),

    html.Div([
        html.Ul([
            # 프로젝트/홈페이지 명
            html.A([
                html.Div(['FDA Project Team',html.Sup('3')],className="sidebar-brand-text mx-3")
            ],href='/', className = "sidebar-brand d-flex align-items-center justify-content-center"),

            # Divider
            html.Hr(className="sidebar-divider my-0"),

            # Nav Item - Dashboard
            html.Li([
                html.A([
                    html.I(className="fas fa-fw fa-tachometer-alt"),
                    html.Span('Dashboard')
                ],href='/',className = "nav-link")
            ], className = "nav-item active"),

            # Divider
            html.Hr(className="sidebar-divider"),

            # Heading
            html.Div('Settings',className="sidebar-heading"),

            # Nav Item - Pages Collapse Menu
            html.Li([
                html.A([
                    html.I(className="fas fa-fw fa-table"),
                    html.Span("주식 매수/매도"),
                ],className="nav-link", href="/stock-list"),
            ],className="nav-item"),

            # Divider
            html.Hr(className="sidebar-divider"),

            # Heading
            html.Div('Test',className="sidebar-heading"),

             # Nav Item - Pages Collapse Menu
            html.Li([
                html.A([
                    html.I(className="fas fa-fw fa-wrench"),
                    html.Span("EWMA"),
                ],className="nav-link", href="/ewma"),
            ],className="nav-item"),

            # Nav Item - Pages Collapse Menu
            html.Li([
                html.A([
                    html.I(className="fas fa-fw fa-chart-area"),
                    html.Span("MV-Model"),
                ],className="nav-link", href="/mv-model"),
            ],className="nav-item"),

            # Nav Item - Pages Collapse Menu
            html.Li([
                html.A([
                    html.I(className="fas fa-fw fa-wrench"),
                    html.Span("BackTest"),
                ],className="nav-link", href="/backtest"),
            ],className="nav-item"),

            # Divider
            html.Hr(className="sidebar-divider d-none d-md-block"),

            # Sidebar Toggler (Sidebar)
            html.Div(
                html.Button(className="rounded-circle border-0",id="sidebarToggle"),
                className="text-center d-none d-md-inline"),

            # End of Sidebar
        ], className = "navbar-nav bg-gradient-primary sidebar sidebar-dark accordion", id="accordionSidebar"),
    
        # Content Wrapper
        html.Div(id="content-wrapper", className="d-flex flex-column"),

    ],id="wrapper"),
    # Scroll to Top Button
    html.A(html.I(className="fas fa-angle-up"),className="scroll-to-top rounded", href="#page-top")
],id="page-top")



@app.callback(Output('content-wrapper', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/stock-list':
        return stock_list_layout
    elif pathname == '/mv-model':
        return mv_model_layout
    elif pathname == '/backtest':
        return backtest_layout
    elif pathname == '/ewma':
        return ewma_layout
    return dashboard_layout

@app.callback(
    Output('dashboard-monthly-return','children'),
    Output('dashboard-total-profit','children'),
    Output('dashboard-realized-profit','children'),
    Input('local_stocklist','data'),
)
def update_return(stl):
    if len(stl) == 0:
        return '$0', '$0', '$0'
    return '$'+str(get_monthly_return(stl).round(2)),'$'+str(get_total_profit(stl).round(2)),'$'+str(get_realized_profit(stl))

STOCK_HAVE = dict()
@app.callback(Output('local_stocklist', 'data'),
            Input('stocklist-submit', 'n_clicks'),
            State('stocklist-dropdown','value'),
            State('stocklist-datepicker','date'),
            State('stocklist-tradeamount','value'),
            State('stocklist-tradevalue','value'),
            State('stocklist-tradetype','value'),
            State('local_stocklist','data')
)
def update_local_stocklist_store(n_clicks, dd, date, tra, trv, trt,stock_list):
    if n_clicks:    
        if trt == "buy":
            if dd in STOCK_HAVE.keys():
                STOCK_HAVE[dd] = STOCK_HAVE[dd]+tra
            else:
                STOCK_HAVE[dd]= tra
        else:
            if dd in STOCK_HAVE.keys():
                STOCK_HAVE[dd] = STOCK_HAVE[dd]-tra
            else:
                STOCK_HAVE[dd]= -tra
        stock_list.append([dd,NASDAQ_DICT[dd],date,tra,trv,trt,STOCK_HAVE[dd]])
        return stock_list
    if len(stock_list) != 0:
        for s in stock_list:
            if s[5] == "buy":
                if s[0] in STOCK_HAVE.keys():
                    STOCK_HAVE[s[0]] = STOCK_HAVE[s[0]]+s[3]
                else:
                    STOCK_HAVE[s[0]]= s[3]
            else:
                if s[0] in STOCK_HAVE.keys():
                    STOCK_HAVE[s[0]] = STOCK_HAVE[s[0]]-s[3]
                else:
                    STOCK_HAVE[s[0]]= -s[3]
        return stock_list
    return []

@app.callback(
    Output("dashboard-stock-graph","figure"),
    Output("dashboard-stock-donut","figure"),
    Input('local_stocklist','data')
)
def update_stock_graph(stock_list):
    symbols = list(set([trade[0] for trade in stock_list]))
    df = all_df[symbols]
    datas=[]
    for s in symbols:
        datas.append(go.Line(x=df.index,y=df[s],name=s))
    if len(STOCK_HAVE)==0:
        sh = dict()
        for s in stock_list:
            if s[5] == "buy":
                if s[0] in sh.keys():
                    sh[s[0]] = sh[s[0]]+s[3]
                else:
                    sh[s[0]]= s[3]
            else:
                if s[0] in sh.keys():
                    sh[s[0]] = sh[s[0]]-s[3]
                else:
                    sh[s[0]]= -s[3]
    else:
        sh = STOCK_HAVE
    labels = list(sh)
    values = get_donut_data(sh)
    return go.Figure(data=datas), go.Figure(data=[go.Pie(labels=labels,values=values,hole=.5,pull=.05)])


@app.callback(Output('stocklist-tbody','children'),
            Input('local_stocklist','data'),
)
def update_stocklist(stock_list):
    stock_list_data = []
    if len(stock_list) == 0:
        return stock_list_data
    n = len(stock_list)
    for i in range(n):
        if stock_list[n-i-1][5] == "buy":
            trt = "매수"
        else:
            trt = "매도"
        stock_list_data.append(html.Tr([
            html.Td(str(n-i)),
            html.Td(stock_list[n-i-1][1]),
            html.Td("$"+str(stock_list[n-i-1][4])),
            html.Td(str(stock_list[n-i-1][3])+"주"),
            html.Td(stock_list[n-i-1][2]),
            html.Td(trt),
            html.Td(str(stock_list[n-i-1][6])+"주"),
        ]))
    return stock_list_data


session_mvmodel_sl = set()
ma_p = 0
md_p = 0
@app.callback(Output('mvmodel-stocklist','children'),
            Input('mvmodel-addstock','n_clicks'),
            Input('mvmodel-delstock','n_clicks'),
            State("mvmodel-stock-selected",'value'),
)
def add_mvmodel_stock(add_c,del_c,val):
    global session_mvmodel_sl, ma_p, md_p
    if val != None:
        if add_c > ma_p:
            session_mvmodel_sl.add(val)
            ma_p = add_c
        elif del_c > md_p:
            session_mvmodel_sl.discard(val)
            md_p = del_c
    return [html.H6(NASDAQ_DICT[i]) for i in session_mvmodel_sl]

@app.callback(Output('mvmodel-constraints-input','children'),
    Input('mvmodel-constraint','value')
)
def change_constraints_input(cons):
    if cons == 'alre':
        return [html.Div([
                    dcc.Input(id='constraints-alre-lowerbound',min=0,max=1,step=0.01,type='number',placeholder="Lower Bound"),
                    dbc.Checklist(id='constraints-alre-weights',labelCheckedStyle={"color": "red"},options=[{"label":i,"value":i} for i in session_mvmodel_sl]),
                    dcc.Input(id='constraints-alre-upperbound',min=0,max=1,step=0.01,type='number',placeholder="Upper Bound"),
                ]),
                dbc.Button([html.Span(html.I(className="fas fa-check"),className="icon text-white-50"),html.Span("바운드 추가하기",className="text")],className="btn btn-secondary btn-icon-split",id='constraints-alre-add'),
                html.Div(id='constraints-alre-addedweights')
            ]
    elif cons == 'trov':
        return [
            dcc.RadioItems(id='constraints-trov-selects',value='each',
            options=[{"label":'Turnover Constraint for each asset',"value":'each'},{"label":'Total Turnover constraint',"value":'sum'}]),
            dcc.Input(id='constraints-trov-turnover',min=0,type='number',placeholder="turn over"),
            dcc.Input(id='constraints-trov-zeroweight',min=0,max=1,type='number',placeholder="weight"),
            dbc.Button([html.Span(html.I(className="fas fa-check"),className="icon text-white-50"),html.Span("weight 추가하기",className="text")],className="btn btn-secondary btn-icon-split",id='constraints-trov-add'),
            html.Div(id='constraints-trov-addedweights')            
            ]
    elif cons == 'trco':
        return [
            dcc.Input(id='constraints-trco-cost',min=0,type='number',placeholder="turn over"),
            dcc.Input(id='constraints-trco-coef',type='number',placeholder="risk coef"),
            dcc.Input(id='constraints-trco-zeroweight',min=0,max=1,type='number',placeholder="weight"),
            dbc.Button([html.Span(html.I(className="fas fa-check"),className="icon text-white-50"),html.Span("weight 추가하기",className="text")],className="btn btn-secondary btn-icon-split",id='constraints-trco-add'),
            html.Div(id='constraints-trco-addedweights')
        ]
    elif cons == 'card':
        return [
            dcc.Input(id='constraints-card-maxnum',min=1,max=len(session_mvmodel_sl),step=1,type='number',placeholder="최대 주식 수"),
            html.Div(id='constraints-card_')
        ]
    elif cons == 'cala':
        return [
            dcc.Input(id='constraints-cala-lambda',type='number',placeholder="lambda"),
            html.Div(id='constraints-cala_')
        ]
    elif cons == 'cael':
        return [
            dcc.Input(id='constraints-cael-lambda1',type='number',placeholder="lambda1"),
            dcc.Input(id='constraints-cael-lambda2',type='number',placeholder="lambda2"),
            html.Div(id='constraints-cael_')
        ]
    elif cons == 'rifc':
        return [
            dcc.Input(id='constraints-rifc-effect',type='number',placeholder="effect"),
            html.Div(id='constraints-rifc_')
        ]
    return []

alre_cons = []
@app.callback(Output('constraints-alre-addedweights','children'),
    Input('constraints-alre-add','n_clicks'),
    State('constraints-alre-lowerbound','value'),
    State('constraints-alre-weights','value'),
    State('constraints-alre-upperbound','value'),
)
def mvmodel_add_bounds(n_clicks,lb,stocks,up):
    def lines():
        result = []
        for con in alre_cons:
            if (con[0] != None) and (con[1] != None):
                result.append(html.H6(str(con[0])+"≤"+' + '.join(con[2])+"≤"+str(con[1])))
            elif con[0] != None:
                result.append(html.H6(str(con[0])+"≤"+' + '.join(con[2])))
            elif con[1] != None:
                result.append(html.H6(' + '.join(con[2])+"≤"+str(con[1])))
        return result
    if stocks != None:
        alre_cons.append([lb,up,stocks])
        
    return lines()

trov_zeroweight = []
trov_index = 0
trov_each = True
trov_turnover_each = []
trov_turnover_sum = 0
@app.callback(
    Output('constraints-trov-addedweights','children'),
    Input('constraints-trov-add','n_clicks'),
    State('constraints-trov-turnover','value'),
    State('constraints-trov-zeroweight','value'),
    State('constraints-trov-selects','value')
)
def mvmodel_add_weight(n_clicks,turnover,weight,select):
    global trov_zeroweight, trov_index, trov_each,trov_turnover_each,trov_turnover_sum
    symbols = list(session_mvmodel_sl)
    if len(trov_zeroweight) != len(symbols):
        trov_zeroweight = [0]*len(symbols)
        trov_turnover_each = [0]*len(symbols)
        trov_index=0
    if select == 'each':
        trov_each = True
        if turnover != None:
            trov_turnover_each[trov_index%len(symbols)] = turnover
    else:
        trov_each = False
        if turnover != None:
            trov_turnover_sum=turnover
    if weight != None:
        if (weight<=1) and (0<=weight):
            trov_zeroweight[trov_index%len(symbols)] = weight
            trov_index += 1
    if select == 'each':
        return [html.H6(NASDAQ_DICT[symbols[i]]+' : '+str(trov_zeroweight[i])+', '+str(trov_turnover_each[i])) for i in range(len(symbols))]
    return [html.H6(NASDAQ_DICT[symbols[i]]+' : '+str(trov_zeroweight[i])) for i in range(len(symbols))]

trco_zeroweight = []
trco_index = 0
trco_cost = []
trco_coef = 0
@app.callback(
    Output('constraints-trco-addedweights','children'),
    Input('constraints-trco-add','n_clicks'),
    State('constraints-trco-cost','value'),
    State('constraints-trco-zeroweight','value'),
    State('constraints-trco-coef','value'),
)
def mvmodel_add_weight(n_clicks,cost,weight,coef):
    global trco_zeroweight, trco_index, trco_cost
    symbols = list(session_mvmodel_sl)
    if len(trco_zeroweight) != len(symbols):
        trco_zeroweight = [0]*len(symbols)
        trco_cost = [0]*len(symbols)
        trco_index=0
    if cost != None:
        trco_cost[trco_index%len(symbols)] = cost
    if coef != None:
        trco_coef = coef
    if weight != None:
        if (weight<=1) and (0<=weight):
            trco_zeroweight[trco_index%len(symbols)] = weight
            trco_index += 1
    return [html.H6(NASDAQ_DICT[symbols[i]]+' : '+str(trco_zeroweight[i])+', '+str(trco_cost[i])) for i in range(len(symbols))]


card_maxasset = 1
@app.callback(Output('constraints-card_','children'),
    Input('constraints-card-maxnum','value')
)
def mvmodel_maxasset(max_asset):
    global card_maxasset
    if max_asset != None:
        card_maxasset = max_asset
    return []

cala_lambda = 0
@app.callback(Output('constraints-cala_','children'),
    Input('constraints-cala-lambda','value')
)
def mvmodel_maxasset(lambda1):
    global cala_lambda
    if lambda1 != None:
        cala_lambda = lambda1
    return []

cael_lambda1 = 0
cael_lambda2 = 0
@app.callback(Output('constraints-cael_','children'),
    Input('constraints-cael-lambda1','value'),
    Input('constraints-cael-lambda1','value')
)
def mvmodel_maxasset(lambda1, lambda2):
    global cael_lambda1,cael_lambda2
    if lambda1 != None:
        cael_lambda1 = lambda1
    if lambda2 != None:
        cael_lambda2 = lambda2
    return []

effect_of_factor = 10**8
@app.callback(Output('constraints-rifc_','children'),
    Input('constraints-rifc-effect','value')
)
def mvmodel_maxasset(effect):
    global effect_of_factor
    if effect != None:
        effect_of_factor = effect
    return []

mvmodel_cons_saved = 'none'
mvmodel_nsh_saved=True
@app.callback(
    Output('mvmodel-result','children'),
    Input('mvmodel-done','n_clicks'),
    State('mvmodel-startdate','date'),
    State('mvmodel-enddate','date'),
    State('mvmodel-constraint','value'),
    State('mvmodel-noshorting','value')
)
def show_mvmodel_result(n_clicks,st,en,cons,nsh):
    global mvmodel_cons_saved, mvmodel_nsh_saved
    mvmodel_cons_saved = cons
    n_sh = False
    if nsh != None:
        if 'n-sh' in nsh:
            n_sh = True
    mvmodel_nsh_saved=n_sh
    if len(session_mvmodel_sl) != 0:
        symbols = list(session_mvmodel_sl)
        if cons == 'alre':
            test_result = mv_opt(data_for_mvopt(symbols,st,en),cons,inputs=alre_cons,nsh=n_sh)
        elif cons == 'trov':
            if trov_each:
                test_result = mv_opt(data_for_mvopt(symbols,st,en),'trov-each',inputs=[trov_zeroweight,trov_turnover_each],nsh=n_sh)
            else:
                test_result = mv_opt(data_for_mvopt(symbols,st,en),'trov-sum',inputs=[trov_zeroweight,trov_turnover_sum],nsh=n_sh)
        elif cons == 'trco':
            test_result = mv_opt(data_for_mvopt(symbols,st,en),cons,inputs=[trco_zeroweight,trco_cost,trco_coef],nsh=n_sh)
        elif cons == 'card':
            test_result = mv_opt(data_for_mvopt(symbols,st,en),cons,inputs=card_maxasset,nsh=n_sh)
        elif cons == 'cala':
            test_result = mv_opt(data_for_mvopt(symbols,st,en),cons,inputs=cala_lambda,nsh=n_sh)
        elif cons == 'cael':
            test_result = mv_opt(data_for_mvopt(symbols,st,en),cons,inputs=[cael_lambda1,cael_lambda2],nsh=n_sh)
        elif cons == 'rifc':
            test_result = mv_opt(data_for_mvopt(symbols,st,en),cons,inputs=effect_of_factor,nsh=n_sh)
        else:
            test_result = mv_opt(data_for_mvopt(symbols,st,en),nsh=n_sh)
        return html.Div([
                        html.Div(
                            html.H6("MV modeling result",className="m-0 font-weight-bold text-primary")
                        ,className="card-header py-3"),
                        html.Div(
                            html.Div(
                                html.Table([
                                    html.Thead(
                                        html.Tr([html.Th(i) for i in symbols])
                                    ),
                                    html.Tbody(
                                        html.Tr([html.Td(i.round(6)) for i in test_result])
                                    ),
                                ],className="table table-bordered", id="dataTable",style={'width':"100%", 'cellspacing':"0"})
                            ,className="table-responsive",style={"overflow": "scroll", "height": "400px"})
                        ,className="card-body")
                    ],className="card shadow mb-4"),
    return []

@app.callback(Output('backtest-stocklist','children'),
            Input('backtest-addstock','n_clicks'),
)
def add_backtest_stock(add_c):
    return [html.H6(NASDAQ_DICT[i]) for i in session_mvmodel_sl]

@app.callback(
    Output('backtest-utbtn','children'),
    Input('backtest-utbtn','n_clicks')
)
def backtest_utbtn_changed(n_clicks):
    if n_clicks%4 == 0:
        return "D"
    elif n_clicks%4 == 1:
        return "W"
    elif n_clicks%4 == 2:
        return "M"
    return"Y"

@app.callback(
    Output('backtest-lbbtn','children'),
    Input('backtest-lbbtn','n_clicks')
)
def backtest_lbbtn_changed(n_clicks):
    if n_clicks%4 == 0:
        return "D"
    elif n_clicks%4 == 1:
        return "W"
    elif n_clicks%4 == 2:
        return "M"
    return"Y"

@app.callback(
    Output('backtest-rbbtn','children'),
    Input('backtest-rbbtn','n_clicks')
)
def backtest_rbbtn_changed(n_clicks):
    if n_clicks%4 == 0:
        return "D"
    elif n_clicks%4 == 1:
        return "W"
    elif n_clicks%4 == 2:
        return "M"
    return"Y"

@app.callback(
    Output("backtest-result","children"),
    Output("backtest-snp-graph",'figure'),
    Output("backtest-snp","children"),
    Input('backtest-done',"n_clicks"),
    State("backtest-startdate",'date'),
    State("backtest-enddate",'date'),
    State('backtest-utinp','value'),
    State('backtest-utbtn',"children"),
    State('backtest-lbinp','value'),
    State('backtest-lbbtn',"children"),
    State('backtest-rbinp','value'),
    State('backtest-rbbtn',"children"),
    State("backtest-dropna",'value')
)
def show_backtest_result(n_clicks,st,en,uti,utb,lbi,lbb,rbi,rbb,drna):
    fig = go.Figure()
    if n_clicks and (len(session_mvmodel_sl)!=0):
        st = datetime(int(st[:4]),int(st[5:7]),int(st[8:10]))
        en = datetime(int(en[:4]),int(en[5:7]),int(en[8:10]))
        ut = timestr_to_datetime(uti,utb)
        lb = timestr_to_datetime(lbi,lbb)
        rb = timestr_to_datetime(rbi,rbb)
        symbols = list(session_mvmodel_sl)
        dna = False
        if drna != None:
            if "dropna" in drna:
                dna = True
        cons = mvmodel_cons_saved
        n_sh=mvmodel_nsh_saved
        if len(session_mvmodel_sl) != 0:
            symbols = list(session_mvmodel_sl)
            if cons == 'alre':
                test_result = backtest(symbols,st,en, ut, lb, rb,cons=cons,inputs=alre_cons,nsh=n_sh)
            elif cons == 'trov':
                if trov_each:
                    test_result = backtest(symbols,st,en, ut, lb, rb,cons='trov-each',inputs=[trov_zeroweight,trov_turnover_each],nsh=n_sh)
                else:
                    test_result = backtest(symbols,st,en, ut, lb, rb,cons='trov-sum',inputs=[trov_zeroweight,trov_turnover_sum],nsh=n_sh)
            elif cons == 'trco':
                test_result = backtest(symbols,st,en, ut, lb, rb,cons=cons,inputs=[trco_zeroweight,trco_cost,trco_coef],nsh=n_sh)
            elif cons == 'card':
                test_result = backtest(symbols,st,en, ut, lb, rb,cons=cons,inputs=card_maxasset,nsh=n_sh)
            elif cons == 'cala':
                test_result = backtest(symbols,st,en, ut, lb, rb,cons=cons,inputs=cala_lambda,nsh=n_sh)
            elif cons == 'cael':
                test_result = backtest(symbols,st,en, ut, lb, rb,cons=cons,inputs=[cael_lambda1,cael_lambda2],nsh=n_sh)
            elif cons == 'rifc':
                test_result = backtest(symbols,st,en, ut, lb, rb,cons=cons,inputs=effect_of_factor,nsh=n_sh)
            else:
                test_result = backtest(symbols,st,en, ut, lb, rb,nsh=n_sh)
            df = test_result
            df['year'] = df.index.year.astype(str)
            df['month'] = df.index.month.astype(str)
            df['month'] = df['month'].apply(lambda x: '0'+x if len(x) == 1 else x)
            df['dateInt']=df['year'].astype(str) + '-' +df['month'].astype(str) + '-01'
            sp = SNP500[SNP500['Date'].isin(df['dateInt'])]
            
            fig.add_trace(go.Scatter(x=df.dateInt, y=df['portfolio_ret'],
                    mode='lines+markers',
                    name='Our_ret'))
            fig.add_trace(go.Scatter(x=sp.Date, y=sp['sp_ret'],
                    mode='lines+markers',
                    name='SP500_ret'))
                    
            pf_ret =df['portfolio_ret'].values
            sp_ret = sp['sp_ret'].values
            snpcol = ['','Annual_return','Annual_variance','sharpe','VaR_95','MDD']
            mean = pf_ret.mean()
            std = pf_ret.std()
            tbport = ['portfolio',mean * 12,std* math.sqrt(12),mean/std,norm.ppf(1-0.9, mean, std),get_mdd(pf_ret)]
            mean = sp_ret.mean()
            std = sp_ret.std()
            tbsnp = ['S&P500',mean * 12,std* math.sqrt(12),mean/std,norm.ppf(1-0.9, mean, std),get_mdd(sp_ret)]
        return html.Div([
                        html.Div(
                            html.H6("Backtest result",className="m-0 font-weight-bold text-primary")
                        ,className="card-header py-3"),
                        html.Div(
                            html.Div(
                                html.Table([
                                    html.Thead(
                                        html.Tr([html.Th(i) for i in (['Date']+[j for j in test_result.columns[:-3]])])
                                    ),
                                    html.Tbody(
                                        [html.Tr([html.Td(index.strftime('%Y/%m/%d'))]+[html.Td(i.round(2)) for i in row[:-3].values.tolist()]) for index, row in test_result.iterrows()]
                                    ),
                                ],className="table table-bordered", id="dataTable",style={'width':"100%", 'cellspacing':"0"})
                            ,className="table-responsive",style={"overflow": "scroll", "height": "400px"})
                        ,className="card-body")
                    ],className="card shadow mb-4"),fig, html.Div([
                        # Content Column
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H6("수익률차트",className="m-0 font-weight-bold text-primary")
                                ],className="card-header py-3"),
                                html.Div(
                                    html.Div(
                                        html.Table([
                                            html.Thead(
                                                html.Tr([html.Th(i) for i in snpcol])
                                            ),
                                            html.Tbody(
                                                [html.Tr([html.Td(i) for i in j]) for j in [tbport,tbsnp]]
                                            ),
                                        ],className="table table-bordered", id="dataTable",style={'width':"100%", 'cellspacing':"0"})
                                    ,className="table-responsive",style={"overflow": "scroll", "height": "400px"})    
                                , className="card-body"),
                            ],className="card shadow mb-4"),
                        ],className="col-xl-12 col-lg-7"),
                    ],className="row")
    return [],fig,[]

@app.callback(Output('ewma_stocks','children'),
    Input('local_stocklist', 'data')
)
def show_ewma_list(stock_list):
    symbols = list(set([trade[0] for trade in stock_list]))
    result = []
    for sym in symbols:
        ew = EWMA(all_df, sym)
        if ew[1]<-0.02:
            result.append(html.Div([
                html.Div(
                    html.Div([
                        NASDAQ_DICT[sym]+" / "+str(ew[0].round(2)),
                        html.Div(str(-(ew[1]*100).round(2))+"% 하락일 것으로 예측됩니다.",className="text-white-50 small")
                    ],className="card-body")
                ,className="card bg-danger text-white shadow")
            ],className="col-lg-3 mb-4"))
        elif ew[1]>0.02:
            result.append(html.Div([
                html.Div(
                    html.Div([
                        NASDAQ_DICT[sym]+" / "+str(ew[0].round(2)),
                        html.Div(str((ew[1]*100).round(2))+"% 상승일 것으로 예측됩니다.",className="text-white-50 small")
                    ],className="card-body")
                ,className="card bg-primary text-white shadow")
            ],className="col-lg-3 mb-4"))
        else:
            result.append(html.Div([
                html.Div(
                    html.Div([
                        NASDAQ_DICT[sym]+" / "+str(ew[0].round(2)),
                        html.Div(str(abs(ew[1]*100).round(2))+"% 유지일 것으로 예측됩니다.",className="text-white-50 small")
                    ],className="card-body")
                ,className="card bg-secondary text-white shadow")
            ],className="col-lg-3 mb-4"))
    return result


be_cl_before = 0
re_cl_before = 0
mi_cl_before = 0
pl_cl_before = 0
ewma_sortby = True
ewma_page = 0
@app.callback(Output('ewma-tbodylist','children'),
    Output('ewma-sortbybeta','children'),
    Output('ewma-sortbyreturn','children'),
    Output('ewma-page','children'),
    Input('ewma-sortbyreturn','n_clicks'),
    Input('ewma-sortbybeta','n_clicks'),
    Input('ewma-page-','n_clicks'),
    Input('ewma-page+','n_clicks'),
)
def ewma_sortbybeta(re_cl,be_cl,mi_cl,pl_cl):
    global be_cl_before, re_cl_before, mi_cl_before, pl_cl_before, ewma_sortby,ewma_page
    if be_cl_before < be_cl:
        be_cl_before = be_cl
        ewma_sortby = True
    if re_cl_before < re_cl:
        re_cl_before = re_cl
        ewma_sortby = False
    if ewma_sortby:
        if be_cl % 2 == 1:
            EWMA_DATA.sort_values(by='beta',ascending=True,inplace=True)
        else:
            EWMA_DATA.sort_values(by='beta',ascending=False,inplace=True)
    else:
        if re_cl % 2 == 1:
            EWMA_DATA.sort_values(by='return',ascending=True,inplace=True)
        else:
            EWMA_DATA.sort_values(by='return',ascending=False,inplace=True)
    if mi_cl_before < mi_cl:
        mi_cl_before = mi_cl
        if ewma_page!=0:
            ewma_page -= 1
    if pl_cl_before < pl_cl:
        pl_cl_before = pl_cl
        if ewma_page!=19:
            ewma_page += 1
    if be_cl % 2 == 1:
        be_ch="▲"
    else:
        be_ch ="▼"
    if re_cl % 2 == 1:
        re_ch="▲"
    else:
        re_ch ="▼"
    return [html.Tr([html.Td(index+1)]+[html.Td(i) for i in row[1:].values.tolist()]) for index, row in EWMA_DATA.iloc[ewma_page*15:(ewma_page+1)*15].iterrows()],be_ch,re_ch,ewma_page+1

if __name__ == '__main__':
    app.run_server(debug=True)