FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/memory-service-0.0.1-SNAPSHOT.jar memory-service.jar

EXPOSE 8086

ENTRYPOINT ["java", "-jar", "memory-service.jar"]
