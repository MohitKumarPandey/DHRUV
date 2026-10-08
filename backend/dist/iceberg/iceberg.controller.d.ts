export declare class IcebergController {
    getIcebergLayer(): {
        layer: string;
        data_quality: string;
    };
    getIceberg(icebergId: string): {
        iceberg_id: string;
        status: string;
    };
    generateForecast(body: any): {
        forecast: string;
        valid_time: Date;
        ensemble: any[];
    };
}
