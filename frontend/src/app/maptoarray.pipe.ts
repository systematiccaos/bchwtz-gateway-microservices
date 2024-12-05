import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'mapToArray'})
export class MapToArrayPipe implements PipeTransform {
  transform(value: any, ...args:string[]) : any {
    let arr = [];
    console.log(value)
    for (let key in value) {
      arr.push({key: key, value: value[key]});
    }
    return arr;
  }
}
