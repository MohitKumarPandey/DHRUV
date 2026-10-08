import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import * as path from 'path';

// Load the proto definition for the Python worker
const PROTO_PATH = path.join(__dirname, '../../../../python/worker/dhruv.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const dhruvProto = grpc.loadPackageDefinition(packageDefinition).dhruv as any;

@Injectable()
export class RoutingService implements OnModuleInit {
  private routingClient: any;
  private readonly logger = new Logger(RoutingService.name);

  onModuleInit() {
    const grpcHost = process.env.GRPC_WORKER_HOST || 'localhost:50051';
    this.logger.log(`Connecting to Python gRPC worker at ${grpcHost}`);
    this.routingClient = new dhruvProto.RoutingService(
      grpcHost,
      grpc.credentials.createInsecure(),
    );
  }

  async generateRoute(payload: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.routingClient.GenerateRoute(payload, (error, response) => {
        if (error) {
          this.logger.error(`gRPC error: ${error.message}`);
          reject(error);
        } else {
          this.logger.log(
            `Route response: status=${response.status}, algo=${response.algorithm}, ` +
            `data_quality=${response.data_quality}, policy=${response.policy_status}`,
          );
          resolve(response);
        }
      });
    });
  }
}
