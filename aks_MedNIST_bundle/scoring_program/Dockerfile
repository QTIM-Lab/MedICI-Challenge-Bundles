FROM python:3.6

# Install vi
RUN apt update -y; apt-get install vim -y;

# Install libraries
RUN pip install scikit-learn

# Default locations for score.py and data
ENV PROGRAM="program"
ENV IN="input"
ENV OUT="output"

CMD "python" "$PROGRAM/score.py" "$IN" "$OUT"