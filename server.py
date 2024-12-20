import logging
from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import TimedRotatingFileHandler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request,Body,Query
import re
from utils.model import call_with_messages,call_with_query, get_res_list,get_order_list
from utils.jd import search_res,get_qq_xy
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@app.post("/jdMsg")
async def msg_format(
        addr: str = Body(..., description="获取订单的地址."),
    ):
    logger.info(f"Received text: {addr}")
    if not addr:
        logger.warning("addr 参数不能为空")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "addr 参数不能为空",
                "result": {}
            }
        )
    status = True
    result = {}
    message = None
    try:
        location = get_qq_xy(addr)
        if not location:
            status = False
            message = '地址解析失败，稍后重试。'
            logger.error("地址解析失败")
        else:

            result = search_res(location['lng'], location['lat'])    
            logger.info("模型解析成功")
    except Exception as e:
        status = False
        message = f'服务器内部错误: {str(e)}'
        logger.error(f"服务器内部错误: {str(e)}")

    return JSONResponse(dict(status=status, message=message, result=result))    

@app.post("/msgFormat")
async def msg_format(
        text: str = Body(..., description="需要格式化的文本."),
    ):
    logger.info(f"Received text: {text}")
    if not text:
        logger.warning("text 参数不能为空")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "text 参数不能为空",
                "result": {}
            }
        )

    status = True
    result = {}
    message = None

    try:
        answer = call_with_query(text)
        if not answer:
            status = False
            message = '模型解析失败，稍后重试。'
            logger.error("模型解析失败")
        else:
            message = 'success'
            res_list = re.findall('###.+?###', answer, re.DOTALL)
                # 循环提取到的任务
            _res = res_list[0]

            work_name_re = re.findall('###客户姓名：(.+?)；', _res)[0]
            work_phone_re = re.findall('客户电话：(.+?)；', _res)[0]
                    
            work_time_re = re.findall('预约时间：(.+?)；', _res)[0]
            work_addr_re = re.findall('预约地址：(.+?)；', _res, re.DOTALL)[0]
            if work_phone_re == '空':
                work_phone_re = ''
                
            result = dict(name=work_name_re,phone=work_phone_re,addr=work_addr_re,work_time=work_time_re,price="70",notes="两小时日常  到手  70",type="日常保洁")
            logger.info("模型解析成功")
    except Exception as e:
        status = False
        message = f'服务器内部错误: {str(e)}'
        logger.error(f"服务器内部错误: {str(e)}")

    return JSONResponse(dict(status=status, message=message, result=result))

from logging.handlers import TimedRotatingFileHandler
def setup_logging():
    logger = logging.getLogger('uvicorn')
    logger.setLevel(logging.INFO)
    
    handler = TimedRotatingFileHandler(
        'app_logs.log', 
        when='midnight', 
        interval=1, 
        backupCount=7
    )
    

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # 添加日志处理器到 logger
    logger.addHandler(handler)
    return logger
logger = setup_logging()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085, log_level="info",workers=1)