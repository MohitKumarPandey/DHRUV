import { RoutingService } from './routing.service';
import { GenerateRouteDto, RouteResponseDto } from './routing.dto';
export declare class RoutingController {
    private readonly routingService;
    private readonly logger;
    constructor(routingService: RoutingService);
    generateRoute(dto: GenerateRouteDto): Promise<RouteResponseDto>;
    getRoute(routeId: string): Promise<{
        route_id: string;
        status: string;
    }>;
    stressTestRoute(routeId: string, body: any): Promise<{
        route_id: string;
        status: string;
        resilience_score: number;
    }>;
    replanRoute(routeId: string, body: any): Promise<{
        route_id: string;
        status: string;
        new_route: any[];
    }>;
}
