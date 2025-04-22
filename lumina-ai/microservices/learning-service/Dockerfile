FROM openjdk:11-jdk-slim

WORKDIR /app

COPY target/learning-service-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 8084

ENTRYPOINT ["java", "-jar", "app.jar"]
