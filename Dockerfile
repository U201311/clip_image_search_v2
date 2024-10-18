FROM python:3.9
# 设置工作目录
WORKDIR /app

# 将当前目录的文件复制到工作目录
COPY . /app

# 安装依赖
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple  -r requirments.txt
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pymongo
RUN pip install  -r requirments.txt
RUN pip install  pymongo
RUN pip install "fastapi[standard]"
RUN pip install uvicorn
EXPOSE 8000

RUN chmod 777 /tmp

CMD ["uvicorn", "main:app", "--reload"]


