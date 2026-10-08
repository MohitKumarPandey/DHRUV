import { OnModuleInit } from '@nestjs/common';
export declare class RoutingService implements OnModuleInit {
    private routingClient;
    private readonly logger;
    onModuleInit(): void;
    generateRoute(payload: any): Promise<any>;
}
