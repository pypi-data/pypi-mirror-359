import os
import cx_Oracle as ora
import oracledb as odb
import sqlalchemy as sqa
from sqlalchemy import create_engine, text
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class ORACLE:
    def __init__(self):
        self._connection_is_valid = None
        self._nome_database = None
        self._cnn = None
        self.__database_error = None

    # ---------------------------------
    def Connect(self, conn: dict):
        msg, result = None, True
        try:

            #region Definindo o tipo de instancia SID/SERVICE_NAME
            if conn["type_conection"].upper() == "SID":
                __dnsName = odb.makedsn(host=conn["host"], port=conn["port"],
                                        sid=conn["instance"])
            else:
                __dnsName = odb.makedsn(host=conn["host"], port=conn["port"],
                                        service_name=conn["instance"])
            #endregion

            #region Tipo de driver de conexao
            """
            Oracle Thin Mode vs Thick Mode no oracledb
            O driver oracledb do Python pode operar em dois modos de conexão com o Oracle Database:            
            . Thin Mode (Padrão) → Conexão nativa, sem necessidade do Oracle Client.
            . Thick Mode → Usa o Oracle Client para recursos avançados e maior desempenho.
            🔹 Comparação Geral
                Característica	                    Thin Mode (Padrão)	Thick Mode
                Requer Oracle Client?	            ❌ Não	            ✅ Sim
                Performance	                           Média	        Alta
                Suporta TNS (tnsnames.ora)?	        ❌ Não   	        ✅ Sim
                Suporta Connection Pooling?	        ❌ Limitado	        ✅ Sim
                Suporte a Banco de Dados Antigos?	❌ Não	            ✅ Sim
                Uso recomendado	                    Ambientes simples	Produção, conexões complexas
                                                    ,Cloud, Containers
            """
            if conn["driver_mode"].upper() == "THICK":
                try:
                    # region LIBRARY
                    if conn["path_library"] is None:
                        __pathlib = os.getenv("ORACLE_LIB")
                    else:
                        __pathlib = conn["path_library"]
                    # endregion
                    ora.init_oracle_client(lib_dir=__pathlib)
                except  Exception as error:
                    ...
                    # Modo THIN apenas do banco 12 em diante
            #endregion

            #region Conexao via SQLALCHEMY | CX_ORACLE | ORACLEDB
            __conn = None
            if conn["driver_conexao"].upper() == "SQLALCHEMY":
                # driver oracledb compativel com banco 12 em diante
                if not conn["driver_library"]:
                    # driver default caso não seja explicitado
                    # para versões do oracle anterior a 12, este driver é o mais recomendado.
                    __driver = "cx_oracle"
                else:
                    __driver = conn["driver_library"].lower()
                conn_cnn = f"""{conn["database"].lower()}+{__driver}://{conn["username"]}:{conn["password"]}@{__dnsName}"""
                __engine = sqa.create_engine(conn_cnn)
                with __engine.connect() as connection:
                    __conn = connection.execute(text("select 1 from dual"))
            elif conn["driver_conexao"].upper() == "CX_ORACLE":
                __conn = ora.connect(conn["username"], conn["password"], __dnsName, threaded=True)
            elif conn["driver_conexao"].upper() == "ORACLEDB" or conn  is None:
                # Conexao via ORACLEDB (Novo driver em substituicao do CX_ORACLE)
                __conn = ora.connect(conn["username"], conn["password"], __dnsName, threaded=True)
            #endregion

            #region Populando propriedadas da classe
            self.CONNECTION = __conn
            self.CONNECTION_VALID = True
            self.DATABASE_ERROR = "Conexao bem sucedida!"""
            self.DATABASE_DRIVER = gen.nvl(conn["driver"], "")
            self.NOME_DATABASE = gen.nvl(conn["database"], "")
            result = True
            #endregion
        except Exception as error:
            self.CONNECTION = False
            self.CONNECTION_VALID = False
            self.DATABASE_ERROR = f"""{json.dumps(conn, indent=4).replace(conn["password"], "******")}\nFalha ao tentar se conectar com o banco de dados ORACLE (SqlAlchemy)\nException Error: {error} """
            self.DATABASE_DRIVER = conn["driver_conexao"]
            self.NOME_DATABASE = conn["database"]
            result = self.CONNECTION
        finally:
            return result

    #region METODOS qQUE FICARÃO DEPRECIADOS A PARTIR DE 18/03/2025
    def Connect_ORA(self, string_connect: dict):
        pathlib, msg, result = None, None, None
        try:
            # Definindo a Library ORACLE
            if "library" in string_connect.keys():
                if string_connect["library"] is None:
                    pathlib = os.getenv("ORACLE_LIB")
                else:
                    pathlib = string_connect["library"]
            else:
                pathlib = os.getenv("ORACLE_LIB")

            # Consistindo se a biblioteca do oracle ja esta iniciada
            try:
                ora.init_oracle_client(lib_dir=pathlib)
            except:
                pass
                # não faz nada (e para deixar assim se nao da erro)

            # Definindo o tipo de instancia SID/SERVICE_NAME
            if string_connect["type_conection"].upper() == "SID":
                dnsName = ora.makedsn(host=string_connect["host"], port=string_connect["port"], sid=string_connect["instance"])
            else:
                dnsName = ora.makedsn(host=string_connect["host"], port=string_connect["port"], service_name=string_connect["instance"])

            # Efetuando a conexao com a instancia do BANCO
            self.CONNECTION = ora.connect(string_connect["username"], string_connect["password"], dnsName, threaded=True)
            self.CONNECTION_VALID = True
            self.NOME_DATABASE = gen.nvl(string_connect["database"], "")
            self.DATABASE_ERROR = "Conexao bem sucedida!"""
            self.DATABASE_DRIVER = gen.nvl(string_connect["database"], "")
            result = self.CONNECTION
        except Exception as error:
            self.CONNECTION = False
            self.CONNECTION_VALID = True
            self.NOME_DATABASE = gen.nvl(string_connect["database"], "")
            self.DATABASE_ERROR = f"""{json.dumps(string_connect, indent=4).replace(string_connect["password"], "******")}\nFalha ao tentar se conectar com o banco de dados ORACLE\nException Error: {error} """
            self.DATABASE_DRIVER = gen.nvl(string_connect["database"], "")
            result = self.DATABASE_ERROR
        finally:
            return result

    def Connect_SQLA(self, string_connect: dict):
        conn = None
        try:
            # Definindo a Library ORACLE
            if string_connect["path_library"] is None:
                # ORACLE_LIB tem que estar previamente criada
                pathlib = os.getenv("ORACLE_LIB")
            else:
                pathlib = string_connect["path_library"]

            # Consistindo se a biblioteca do oracle ja esta iniciada
            try:
                ora.init_oracle_client(lib_dir=pathlib)
            except:
                pass
                # não faz nada (e para deixar assim se nao da erro)
            # Validando se foi passado um driver para conexao
            if string_connect["driver_conexao"] is None:
                string_connect["driver_conexao"] = "cx_oracle"
            database = string_connect["database"]
            driver = string_connect["driver_conexao"]
            user = string_connect["username"]
            pwd = string_connect["password"]
            host = string_connect["host"]
            port = string_connect["port"]
            string_connect["instance"] = ora.makedsn(host, port, string_connect["instance"])
            # Validando o tipo de conexao (SID ou SERVICE_NAME) apenas oracle
            if string_connect["type_conection"].upper() == "SERVICE_NAME":
                string_connect["instance"] = string_connect["instance"].replace("SID", "SERVICE_NAME")
            dnsName = string_connect["instance"]
            str_cnn = f"""{database.lower()}{driver}://{user}:{pwd}@{dnsName}"""
            engine = sqa.create_engine(str_cnn)
            with engine.connect() as connection:
                self.CONNECTION = connection.execute(text("Select 1 from dual"))
                self.CONNECTION_VALID = True
                self.DATABASE_ERROR = "Conexao bem sucedida!"""
                self.DATABASE_DRIVER = gen.nvl(string_connect["database"], "")
                result = self.CONNECTION
        except Exception as error:
            msg = f"""{json.dumps(string_connect, indent=4).replace(string_connect["password"], "******")}\nFalha ao tentar se conectar com o banco de dados ORACLE (SqlAlchemy)\nException Error: {error} """
            self.CONNECTION = False
            self.CONNECTION_VALID = False
            self.DATABASE_ERROR = msg
            self.NOME_DATABASE = gen.nvl(string_connect["database"], "")
            result = self.CONNECTION
        finally:
            return result
    #endregion

        # region PROPRIEDADES
        @property
        def CONNECTION(self):
            return self.__cnn

        @property
        def CONNECTION_VALID(self):
            return self.__connection_is_valid

        @property
        def NOME_DATABASE(self):
            return self.__nome_database.upper()

        @property
        def DATABASE_ERROR(self):
            return self.__database_error

        @property
        def DATABASE_DRIVER(self):
            return self.__database_driver

        @CONNECTION.setter
        def CONNECTION(self, value):
            self.__cnn = value

        @CONNECTION_VALID.setter
        def CONNECTION_VALID(self, value):
            self._connection_is_valid = value

        @NOME_DATABASE.setter
        def NOME_DATABASE(self, value):
            self._nome_database = value

        @DATABASE_ERROR.setter
        def DATABASE_ERROR(self, value):
            self.__database_error = value

        @DATABASE_DRIVER.setter
        def DATABASE_DRIVER(self, value):
            self.__database_driver = value

    # endregion