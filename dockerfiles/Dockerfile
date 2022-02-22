FROM apache/airflow:2.1.1-python3.8
USER root
RUN apt-get update && apt-get install -y wget tar nano && apt-get autoremove && apt-get autoclean

# Install OpenJDK-11
RUN apt-get install -y openjdk-11-jdk ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

# SPARK installation

RUN wget https://dlcdn.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz \
&& tar xvf spark-3.2.1-bin-hadoop3.2.tgz \
&& mv spark-3.2.1-bin-hadoop3.2/ /opt/spark \
&& rm -r /opt/airflow/spark-3.2.1-bin-hadoop3.2.tgz

RUN echo 'export SPARK_HOME=/opt/spark' >> ~/.bashrc  \
    && echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> ~/.bashrc

RUN source ~/.bashrc

USER ${AIRFLOW_UID}:${AIRFLOW_GID}
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements_airflow.txt


#COPY create_user.sh /
#RUN chmod +x create_user.sh
#ENTRYPOINT ["/usr/bin/dumb-init", "--", "/create_user.sh"]