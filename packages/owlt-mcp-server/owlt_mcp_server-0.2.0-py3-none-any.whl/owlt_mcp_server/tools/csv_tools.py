from owlt_mcp_server.server import mcp
from owlt_mcp_server.utils.trans_func import uni_translate
from owlt_mcp_server.utils.trans_func import dseek_translate
from owlt_mcp_server.utils.trans_func import lara_translate
from owlt_mcp_server.utils.yd_func import yd_text_translate
from owlt_mcp_server.utils.yddoc import yddoc_process

@mcp.tool()
def translate_text(text: str, language: str) ->str:
    return uni_translate(text, language)
    
    
    
@mcp.tool()
def use_deepseek_translate(text: str, language: str) ->str:
    return dseek_translate(text, language)
    
@mcp.tool()
def use_lara(text: str, language: str) ->str:
    return lara_translate(text, language)
    
    
@mcp.tool()
def use_youdao_translate(text: str, language: str) ->str: 
    return yd_text_translate(text, language)
    
    
@mcp.tool(title="youdao document translator")
async def document_translate(filepath: str, langFrom: str, langTo: str) -> str:
    return yddoc_process(filepath, langFrom, langTo)