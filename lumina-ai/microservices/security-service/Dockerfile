FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/security-service-0.0.1-SNAPSHOT.jar security-service.jar

EXPOSE 8085

ENTRYPOINT ["java", "-jar", "security-service.jar"]
