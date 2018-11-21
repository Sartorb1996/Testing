import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';



export interface Bar {
  barname: string;
  lic: string;
  city: string;
  phone: string;
  addr: string;
}

export interface BarMenuItem {
  beer: string;
  manf: string;
  price: number;
  likes: number;
}

export interface TopTen {
  drinker: string;
  spent: string
}


@Injectable({
  providedIn: 'root'
})
export class BarsService {

  constructor(
    public http: HttpClient
  ) {
  }

  getBars() {
    return this.http.get<Bar[]>('/api/bar');
  }

  getBar(bar: string) {
    return this.http.get<Bar>('/api/bar/' + bar);
  }

  getMenu(bar: string) {
    return this.http.get<BarMenuItem[]>('/api/menu/' + bar);
  }

  getFrequentCounts() {
    return this.http.get<any[]>('/api/frequents-data');
  }

  getTopTen(bar: string) {
    return this.http.get<TopTen[]>('/api/bar/' + bar + '/topten');
  }

  getTopBeers(bar: string) {
    return this.http.get<any[]>('/api/bar/' + bar + '/topbeers');
  }
  getTopManf(bar: string) {
    return this.http.get<any[]>('/api/bar/' + bar + '/topmanf');
  }

  getSalesByTime(bar: string) {
    return this.http.get<any[]>('/api/bar/' + bar + '/bytime');
  }

  getSalesByDay(bar: string) {
    return this.http.get<any[]>('/api/bar/' + bar + '/byday');
  }

}


