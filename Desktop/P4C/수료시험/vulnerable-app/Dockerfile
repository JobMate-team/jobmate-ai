# 빌드 스테이지
FROM maven:3.6.3-jdk-8 AS build
COPY src /home/app/src
COPY pom.xml /home/app
RUN mvn -f /home/app/pom.xml clean package

# 패키지 스테이지
FROM openjdk:8-jdk-alpine
COPY --from=build /home/app/target/*.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
