// The JSON is canonical; unknowns are null, and source IDs refer to the sources table.
export type Source = {id:string;type:string;title:string;url:string|null;description:string;[key:string]:unknown};
export type DateValue = {value:string|null;precision:string|null;calendar:string;hebrew:string|null;source_ids:string[];note:string|null};
export type LifeEvent = {date:DateValue;place:{label:string;geo:null}|null;source_ids:string[]};
export type Person = {id:string;names:{display:string;given:string;surname_birth:string|null;hebrew:{full:string|null}};sex:{value:'male'|'female'|'unknown'};living:{status:string};generation:number;relationships:{parent_ids:string[];spouse_ids:string[];child_ids:string[];sibling_ids:string[]};life_events:{birth:LifeEvent;death:LifeEvent|null};facts:{field:string;value:string;kind:'user_stated'|'public_record'|'inference'|'family_verified';source_ids:string[];note:string|null}[];source_ids:string[];[key:string]:unknown};
export type Union = {id:string;partner_ids:string[];child_ids:string[];events:{wedding:LifeEvent|null};[key:string]:unknown};
export type Tree = {meta:{title:string;format_version:string;focus_person_id:string;[key:string]:unknown};statistics:{persons:number;sources:number;generations:number};persons:Person[];unions:Union[];sources:Source[];events:unknown[];open_questions:unknown[];research_leads:unknown[]};
export function indexTree(tree:Tree){return {people:new Map(tree.persons.map(p=>[p.id,p])),unions:new Map(tree.unions.map(u=>[u.id,u])),sources:new Map(tree.sources.map(s=>[s.id,s]))};}
