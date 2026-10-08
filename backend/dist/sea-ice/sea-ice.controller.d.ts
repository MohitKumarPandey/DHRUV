export declare class SeaIceController {
    getSeaIceLayer(): {
        layer: string;
        data_quality: string;
    };
    generateForecast(body: any): {
        forecast: string;
        valid_time: Date;
        data_quality: string;
    };
}
