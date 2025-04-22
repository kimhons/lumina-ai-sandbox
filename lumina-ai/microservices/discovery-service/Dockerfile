FROM openjdk:17-slim

WORKDIR /app

COPY target/discovery-service-0.1.0-SNAPSHOT.jar app.jar

EXPOSE 8761

ENTRYPOINT ["java", "-jar", "app.jar"]
