FROM python:3.12
WORKDIR /root

# Install the application dependencies
COPY . /root
RUN pip3 install -r requirements.txt

CMD ["python3", "bot.py", "KEY_GOES_HERE"]