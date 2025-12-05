export interface I_api_response {
    error_code: number;
    message: string;

}
export interface I_api_list_response extends I_api_response {
    count: number;
    page: number;
    size: number;
}
