FROM openjdk:17-slim

WORKDIR /app

COPY target/api-gateway-0.1.0-SNAPSHOT.jar app.jar

EXPOSE 8000

ENTRYPOINT ["java", "-jar", "app.jar"]
