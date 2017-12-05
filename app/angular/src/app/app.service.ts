import { Injectable } from "@angular/core";
import { Http, URLSearchParams, Headers, Response } from '@angular/http';
import { HttpClient } from '@angular/common/http';
import { Observable } from "rxjs/Observable";
import { map } from 'rxjs/operators';

import { baseUrl } from "./settings";
import { CameraSettings } from "./model/points-settings";
import { ClusterSettings, DBSCAN, MeanShift } from "./model/cluster-algorithm";
import { Subject, BehaviorSubject } from "rxjs";

@Injectable()
export class AppService {

    selectedModel: Subject<string> = new BehaviorSubject<string>(null);
    
    constructor(private _http: Http, private _httpClient: HttpClient) {}

    getClusters(pointcloud: number[][], clusterSettings: ClusterSettings): Observable<Response> {
        let body = new FormData();
        if (typeof pointcloud != 'undefined' 
            && typeof clusterSettings != 'undefined') {
            body.append('pointcloud', JSON.stringify(pointcloud));
            for (let key in clusterSettings.cluster) {
                body.append(key, clusterSettings.cluster[key].toString());
                console.log(key + "  ", clusterSettings.cluster[key].toString())
            }
            return this._http.post(`${baseUrl}/cluster`, body);
        }
        throw new TypeError("None of pointcloud or clusterSettings allowed to be 'undefined'");
    }

    getPoints(filename: string): Observable<Response> {
        return this._http.get(`${baseUrl}/plot/points/${filename}`);
    }

    getCameraSettings(pointcloud: Array<Array<number>>, voxels, name): Observable<CameraSettings> {
        if ((typeof pointcloud == 'undefined' 
            && typeof voxels == 'undefined')
            && typeof name != 'undefined') {
            throw new TypeError("Invalid Input, please provide points or voxels. name is not allowed to be 'undefined'"); 
        }
        let body = new FormData();
        body.append('name', name);
        typeof pointcloud != 'undefined' ? body.append('pointcloud', JSON.stringify(pointcloud)) : null;
        typeof voxels != 'undefined' ? body.append('voxels', voxels) : null;
        return this._httpClient.post<CameraSettings>(`${baseUrl}/plot/settings`, body);
    }

    predict(pointcloud: number[][], model: string): Observable<Response>  {
        let body = new FormData();
        if (typeof pointcloud != 'undefined') {
            body.append('pointcloud', JSON.stringify(pointcloud));
            body.append('model', model);
        } else {
            throw new TypeError("Point Cloud should be 2d array, not 'undefined'");
        }
        return this._http.post(`${baseUrl}/predict`, body);
    }

    getModels(): Observable<Response>  {
        return this._http.get(`${baseUrl}/models`);
    }

}