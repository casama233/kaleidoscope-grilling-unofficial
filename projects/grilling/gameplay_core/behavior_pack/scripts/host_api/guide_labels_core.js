export const GUIDE_CAPABILITIES=Object.freeze(['guidebook_localized_labels_v1']);
/** Small public guide capability: keep the author's renderer and navigation. */
const methods={
 'Hand Threading':['手工穿串','手工穿串','Hand Threading'],
 'Grill':['烧烤架','燒烤架','Grill'],
 'Chopping Board':['砧板','砧板','Chopping Board'],
 'Millstone':['磨石','磨石','Millstone'],
 'Wok':['炒锅','炒鍋','Wok'],
 'Stockpot':['汤锅','湯鍋','Stockpot'],
 'Oil Press':['榨油器','榨油器','Oil Press'],
 'Big Vat':['大缸','大缸','Big Vat']
};
export function publicMethodLabel(method,locale){const labels=methods[method];return labels?.[locale==='zh_CN'?0:locale==='zh_TW'?1:2];}
export function publicExtensionName(extension,locale,id){const value=extension?.names?.[locale]?.[id];return typeof value==='string'&&value?value:undefined;}
