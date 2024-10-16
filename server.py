import grpc
import time
from concurrent import futures
import protos.phone_pb2 as phone_pb2
import protos.phone_pb2_grpc as phone_pb2_grpc

class GPSTrackerService(phone_pb2_grpc.TelemetryServiceServicer):
    
    def SetTelemetryStream(self, request_iterator, context):
        for telemetry in request_iterator:
            print(f"Установлено соединение с пользователем {telemetry.user_id}",
                  f"координаты: N{telemetry.location.latitude} E{telemetry.location.longitude}")
        option = int(input("нажмите '1' чтобы получить текущее местоположение,"
                            "нажмите '2' чтобы получить перемещение пользователя: "))
        algorithm = int(input("Если хотите поменять алгоритм вычисления координат нажмите '3',"
                              "чтобы оставить текущий алгоритм нажмите '4': "))
        if algorithm == 3:
            yield self.AckComand(alg=algorithm)
        yield self.AckComand(option)


    def AckComand(self, option=None, alg=4):
        if option is None and alg == 3:
            response = phone_pb2.TelemetryStreamCommand(
                ack=phone_pb2.TelemetryStreamCommand.Ack()
            )
        if option == 1:
            response = phone_pb2.TelemetryStreamCommand(
                get_one=phone_pb2.TelemetryStreamCommand.GetOne()
            )
            
        elif option == 2:
            duration = int(input("Введите количество секунд передачи данных: "))
            response = phone_pb2.TelemetryStreamCommand(
                start=phone_pb2.TelemetryStreamCommand.Start(duration=duration),
            )
        return response
        
            
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    phone_pb2_grpc.add_TelemetryServiceServicer_to_server(GPSTrackerService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
