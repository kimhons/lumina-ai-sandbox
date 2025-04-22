FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/collaboration-service-0.0.1-SNAPSHOT.jar collaboration-service.jar

EXPOSE 8087

ENTRYPOINT ["java", "-jar", "collaboration-service.jar"]
