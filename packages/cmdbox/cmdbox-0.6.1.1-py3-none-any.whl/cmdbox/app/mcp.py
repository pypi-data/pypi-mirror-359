from cmdbox.app import common, options
from cmdbox.app.options import Options
from cmdbox.app.auth import signin
from pathlib import Path
from typing import Callable, List, Dict, Any, Tuple
import argparse
import logging
import locale
import json
import time
import re
import os


class Mcp:
    default_host:str = os.environ.get('REDIS_HOST', 'localhost')
    default_port:int = int(os.environ.get('REDIS_PORT', '6379'))
    default_pass:str = os.environ.get('REDIS_PASSWORD', 'password')
    default_svname:str = os.environ.get('SVNAME', 'server')

    def __init__(self, logger:logging.Logger, data:Path, sign:signin.Signin, appcls=None, ver=None,):
        """
        MCP (Multi-Channel Protocol) クラスの初期化

        Args:
            logger (logging.Logger): ロガー
            data (Path): データのパス
            sign (signin.Signin): サインインオブジェクト
            appcls (type, optional): アプリケーションクラス. Defaults to None.
            ver (module, optional): バージョンモジュール. Defaults to None.
        """
        self.logger = logger
        self.data = data
        self.appcls = appcls
        self.ver = ver
        self.signin = sign

    def create_mcpserver(self, args:argparse.Namespace) -> Any:
        """
        mcpserverを作成します

        Args:
            args (argparse.Namespace): 引数

        Returns:
            Any: FastMCP
        """
        from fastmcp import FastMCP
        from fastmcp.server.auth import BearerAuthProvider
        cls = self.signin.__class__
        publickey_str = cls.verify_jwt_publickey_str if hasattr(cls, 'verify_jwt_publickey_str') else None
        issuer = cls.verify_jwt_issuer if hasattr(cls, 'verify_jwt_issuer') else None
        audience = cls.verify_jwt_audience if hasattr(cls, 'verify_jwt_audience') else None
        if publickey_str is not None and issuer is not None and audience is not None:
            self.logger.info(f"Using BearerAuthProvider with public key, issuer: {issuer}, audience: {audience}")
            auth = BearerAuthProvider(
                public_key=publickey_str,
                issuer=issuer,
                audience=audience
            )
            mcp = FastMCP(name=self.ver.__appid__, auth=auth)
        else:
            self.logger.info(f"Using BearerAuthProvider without public key, issuer, or audience.")
            mcp = FastMCP(name=self.ver.__appid__)
        return mcp

    def create_session_service(self, args:argparse.Namespace) -> Any:
        """
        セッションサービスを作成します

        Args:
            args (argparse.Namespace): 引数

        Returns:
            BaseSessionService: セッションサービス
        """
        from google.adk.events import Event
        from google.adk.sessions import DatabaseSessionService, InMemorySessionService, session
        from typing_extensions import override
        if hasattr(args, 'agent_session_dburl') and args.agent_session_dburl is not None:
            class _DatabaseSessionService(DatabaseSessionService):
                @override
                async def append_event(self, session: session.Session, event: Event) -> Event:
                    # 永続化されるセッションには <important> タグを含めない
                    bk_parts = event.content.parts.copy()
                    for part in event.content.parts:
                        if not part.text: continue
                        part.text = re.sub(r"<important>.*</important>", "", part.text)
                    for part in bk_parts:
                        if not part.text: continue
                        part.text = part.text.replace("<important>", "").replace("</important>", "")
                    ret = await super().append_event(session, event)
                    ret.content.parts = bk_parts
                    return ret
            dss = _DatabaseSessionService(db_url=args.agent_session_dburl)
            #dss.db_engine.echo = True
            return dss
        else:
            return InMemorySessionService()

    def create_agent(self, logger:logging.Logger, args:argparse.Namespace, tools:List[Callable]) -> Any:
        """
        エージェントを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tools (List[Callable]): 関数

        Returns:
            Agent: エージェント
        """
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent processing..")
        language, _ = locale.getlocale()
        is_japan = language.find('Japan') >= 0 or language.find('ja_JP') >= 0
        description = f"{self.ver.__appid__}に登録されているコマンド提供"
        instruction = f"あなたはコマンドの意味を熟知しているエキスパートです。" + \
                      f"ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを確実に実行してください。\n" + \
                      f"1. ユーザーのクエリからが実行したいコマンドを特定します。\n" + \
                      f"2. コマンド実行に必要なパラメータのなかで、ユーザーのクエリから取得できないものは、コマンド定義にあるデフォルト値を指定して実行してください。\n" + \
                      f"3. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。\n"

        description = description if is_japan else \
                      f"Command offer registered in {self.ver.__appid__}."
        instruction = instruction if is_japan else \
                      f"You are the expert who knows what the commands mean." + \
                      f"When a user wants to execute a command, you follow these steps to ensure that the command is executed.\n" + \
                      f"1. Identify the command you want to execute from the user's query.\n" + \
                      f"2. Any parameters required to execute the command that cannot be obtained from the user's query should be executed with the default values provided in the command definition.\n" + \
                      f"3. If an error occurs, provide the user with the command name, parameters, and error description.\n"

        description = args.agent_description if args.agent_description else description
        instruction = args.agent_instruction if args.agent_instruction else instruction
        if logger.level == logging.DEBUG:
            logger.debug(f"google-adk loading..")
        from google.adk.agents import Agent
        if logger.level == logging.DEBUG:
            logger.debug(f"litellm loading..")
        from google.adk.models.lite_llm import LiteLlm
        # loggerの初期化
        common.reset_logger("LiteLLM Proxy")
        common.reset_logger("LiteLLM Router")
        common.reset_logger("LiteLLM")
        if args.llmprov == 'openai':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmapikey is None: raise ValueError("llmapikey is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=args.llmmodel,
                    api_key=args.llmapikey,
                    endpoint=args.llmendpoint,
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        elif args.llmprov == 'azureopenai':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmendpoint is None: raise ValueError("llmendpoint is required.")
            if args.llmapikey is None: raise ValueError("llmapikey is required.")
            if args.llmapiversion is None: raise ValueError("llmapiversion is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=args.llmmodel,
                    api_key=args.llmapikey,
                    endpoint=args.llmendpoint,
                    api_version=args.llmapiversion,
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        elif args.llmprov == 'vertexai':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmlocation is None: raise ValueError("llmlocation is required.")
            if args.llmsvaccountfile is not None: 
                with open(args.llmsvaccountfile, "r", encoding="utf-8") as f:
                    vertex_credentials = json.load(f)
            elif args.llmprojectid is None: raise ValueError("llmprojectid is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=args.llmmodel,
                    #vertex_project=args.llmprojectid,
                    vertex_credentials=vertex_credentials,
                    vertex_location=args.llmlocation,
                    #seed=args.llmseed,
                    #temperature=args.llmtemperature,
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        elif args.llmprov == 'ollama':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmendpoint is None: raise ValueError("llmendpoint is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=f"ollama/{args.llmmodel}",
                    api_base=args.llmendpoint,
                    temperature=args.llmtemperature,
                    stream=True
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        else:
            raise ValueError("llmprov is required.")
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent complate.")
        return agent

    def create_runner(self, logger:logging.Logger, args:argparse.Namespace, session_service, agent) -> Any:
        """
        ランナーを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            session_service (BaseSessionService): セッションサービス
            agent (Agent): エージェント

        Returns:
            Runner: ランナー
        """
        from google.adk.runners import Runner
        return Runner(
            app_name=self.ver.__appid__,
            agent=agent,
            session_service=session_service,
        )

    def init_agent_runner(self, logger:logging.Logger, args:argparse.Namespace) -> Tuple[Any, Any]:
        """
        エージェントの初期化を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            Tuple[Any, Any]: ランナーとFastMCP
        """
        if logger.level == logging.DEBUG:
            logger.debug(f"init_agent_runner processing..")
        # loggerの初期化
        common.reset_logger("httpx")
        common.reset_logger("google_adk.google.adk.sessions.database_session_service")
        common.reset_logger("mcp.server.streamable_http_manager")
        # モジュールインポート
        from fastmcp import FastMCP
        from google.adk.sessions import BaseSessionService
        mcp:FastMCP = self.create_mcpserver(args)
        session_service:BaseSessionService = self.create_session_service(args)
        options = Options.getInstance()
        tools:Callable[[logging.Logger, argparse.Namespace, float, Dict], Tuple[int, Dict[str, Any], Any]] = []

        def _ds(d:str) -> str:
            return f'"{d}"' if d is not None else 'None'
        def _t2s(o:Dict[str, Any], req=True) -> str:
            t, m, d, r = o["type"], o["multi"], o["default"], o["required"]
            if t == Options.T_BOOL: return ("List[bool]=[]" if m else f"bool={d}") if req else ("List[bool]" if m else f"bool")
            if t == Options.T_DATE: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_DATETIME: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_DICT: return ("List[dict]=[]" if m else f"dict={d}") if req else ("List[dict]" if m else f"dict")
            if t == Options.T_DIR or t == Options.T_FILE:
                if d is not None: d = str(d).replace('\\', '/')
                return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_FLOAT: return ("List[float]=[]" if m else f"float={d}") if req else ("List[float]" if m else f"float")
            if t == Options.T_INT: return ("List[int]=[]" if m else f"int={d}") if req else ("List[int]" if m else f"int")
            if t == Options.T_STR: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_TEXT: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            raise ValueError(f"Unknown type: {t} for option {o['opt']}")
        def _arg(o:Dict[str, Any], is_japan) -> str:
            t, d = o["type"], o["default"]
            s = f'        {o["opt"]}:'
            if t == Options.T_DIR or t == Options.T_FILE:
                d = str(d).replace("\\", "/")
            s += f'{_t2s(o, False)}={d}:'
            #s += f'Optional[{_t2s(o, False)}]={d}:'
            s += f'{o["discription_ja"] if is_japan else o["discription_en"]}'
            return s
        def _coercion(a:argparse.Namespace, key:str, dval) -> str:
            dval = f'opt["{key}"] if "{key}" in opt else ' + f'"{dval}"' if isinstance(dval, str) else dval
            aval = args.__dict__[key] if hasattr(args, key) and args.__dict__[key] else None
            aval = f'"{aval}"' if isinstance(aval, str) else aval
            ret = f'opt["{key}"] = {aval}' if aval is not None else f'opt["{key}"] = {dval}'
            return ret
        language, _ = locale.getlocale()
        is_japan = language.find('Japan') >= 0 or language.find('ja_JP') >= 0
        for mode in options.get_mode_keys():
            for cmd in options.get_cmd_keys(mode):
                if not options.get_cmd_attr(mode, cmd, 'use_agent'):
                    continue
                discription = options.get_cmd_attr(mode, cmd, 'discription_ja' if is_japan else 'discription_en')
                choices = options.get_cmd_choices(mode, cmd, False)
                if len([opt for opt in choices if 'opt' in opt and opt['opt'] == 'signin_file']) <= 0:
                    choices.append(dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=True, choice=None,
                        discription_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。",
                        discription_en="Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."),)
                fn = f"{mode}_{cmd}"
                func_txt  = f'def {fn}(' + ", ".join([f'{o["opt"]}:{_t2s(o, False)}' for o in choices]) + '):\n'
                func_txt += f'    """\n'
                func_txt += f'    {discription}\n'
                func_txt += f'    Args:\n'
                func_txt += "\n".join([_arg(o, is_japan) for o in choices])
                func_txt += f'\n'
                func_txt += f'    Returns:\n'
                func_txt += f'        Dict[str, Any]:{"処理結果" if is_japan else "Processing Result"}\n'
                func_txt += f'    """\n'
                func_txt += f'    scope = signin.get_request_scope()\n'
                func_txt += f'    logger = common.default_logger()\n'
                func_txt += f'    opt = dict()\n'
                func_txt += f'    opt["mode"] = "{mode}"\n'
                func_txt += f'    opt["cmd"] = "{cmd}"\n'
                func_txt += f'    opt["data"] = opt["data"] if hasattr(opt, "data") else common.HOME_DIR / ".{self.ver.__appid__}"\n'
                func_txt += f'    opt["format"] = False\n'
                func_txt += f'    opt["output_json"] = None\n'
                func_txt += f'    opt["output_json_append"] = False\n'
                func_txt += f'    opt["debug"] = logger.level == logging.DEBUG\n'
                func_txt += '\n'.join([f'    opt["{o["opt"]}"] = {o["opt"]}' for o in choices])+'\n'
                func_txt += f'    {_coercion(args, "host", self.default_host)}\n'
                func_txt += f'    {_coercion(args, "port", self.default_port)}\n'
                func_txt += f'    {_coercion(args, "password", self.default_pass)}\n'
                func_txt += f'    {_coercion(args, "svname", self.default_svname)}\n'
                func_txt += f'    {_coercion(args, "retry_count", 3)}\n'
                func_txt += f'    {_coercion(args, "retry_interval", 3)}\n'
                func_txt += f'    {_coercion(args, "timeout", 15)}\n'
                func_txt += f'    {_coercion(args, "output_json", None)}\n'
                func_txt += f'    {_coercion(args, "output_json_append", False)}\n'
                func_txt += f'    {_coercion(args, "stdout_log", False)}\n'
                func_txt += f'    {_coercion(args, "capture_stdout", False)}\n'
                func_txt += f'    {_coercion(args, "capture_maxsize", 1024*1024)}\n'
                func_txt += f'    {_coercion(args, "tag", None)}\n'
                func_txt += f'    {_coercion(args, "clmsg_id", None)}\n'
                func_txt += f'    opt["signin_file"] = signin_file if signin_file else ".{self.ver.__appid__}/user_list.yml"\n'
                func_txt += f'    args = argparse.Namespace(**opt)\n'
                func_txt += f'    signin_data = signin.Signin.load_signin_file(args.signin_file)\n'
                func_txt += f'    req = scope["req"] if scope["req"] is not None else scope["websocket"]\n'
                func_txt += f'    sign = signin.Signin._check_signin(req, scope["res"], signin_data, logger)\n'
                func_txt += f'    if sign is not None:\n'
                func_txt += f'        logger.warning("Unable to execute command because authentication information cannot be obtained")\n'
                func_txt += f'        return dict(warn="Unable to execute command because authentication information cannot be obtained")\n'
                func_txt += f'    groups = req.session["signin"]["groups"]\n'
                func_txt += f'    logger.info("Call agent tool `{mode}_{cmd}`:user="+str(req.session["signin"]["name"])+" groups="+str(groups)+" args="+str(args))\n'
                func_txt += f'    if not signin.Signin._check_cmd(signin_data, groups, "{mode}", "{cmd}", logger):\n'
                func_txt += f'        logger.warning("You do not have permission to execute this command.")\n'
                func_txt += f'        return dict(warn="You do not have permission to execute this command.")\n'
                func_txt += f'    feat = Options.getInstance().get_cmd_attr("{mode}", "{cmd}", "feature")\n'
                func_txt += f'    try:\n'
                func_txt += f'        st, ret, _ = feat.apprun(logger, args, time.perf_counter(), [])\n'
                func_txt += f'        return ret\n'
                func_txt += f'    except Exception as e:\n'
                func_txt += f'        logger.error("Error occurs when tool is executed:", exc_info=True)\n'
                func_txt += f'        raise e\n'
                func_txt += f'tools.append({fn})\n'
                if logger.level == logging.DEBUG:
                    logger.debug(f"generating agent tool: {fn}")

                exec(func_txt,
                     dict(time=time,List=List, argparse=argparse, common=common, Options=Options, logging=logging, signin=signin,),
                     dict(tools=tools, mcp=mcp))
                exec(f"@mcp.tool\n{func_txt}",
                     dict(time=time,List=List, argparse=argparse, common=common, Options=Options, logging=logging, signin=signin,),
                     dict(tools=[], mcp=mcp))
        root_agent = self.create_agent(logger, args, tools)
        runner = self.create_runner(logger, args, session_service, root_agent)
        if logger.level == logging.DEBUG:
            logger.debug(f"init_agent_runner complate.")
        return runner, mcp
