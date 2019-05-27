
function last(N) {
    return db.Blogs.find().skip(db.Blogs.count()-N);
}

function one() {
    return db.Blogs.findOne();
}

function blogCount() {
    return db.Blogs.aggregate([
        { $group: { _id: null, count: {$sum: 1} } }
    ]);
}

function withArticles() {
    return db.Blogs.aggregate([
        { $match: { "articles_amount" : {$gt : 0}} },
        { $group: { _id: null, count: {$sum: 1} } }
    ]);
}

function withNoArticles() {
    return db.Blogs.aggregate([
        { $match: { "articles_amount" : 0 } },
        { $group: { _id: null, count: {$sum: 1} } }
    ]);
}

function totalNumberOfArticles() {
    return db.Blogs.aggregate([
        { $match: { "articles_amount" : {$gt : 0}} },
        { $group: { _id: null, total: {$sum: "$articles_amount"} } }
    ]);
}

function totalNumberOfViews() {
    return db.Blogs.aggregate([
        { $match: { "views" : {$gt : 0}} },
        { $group: { _id: null, total: {$sum: "$views"} } }
    ]);
}

function totalNumberOfFollowers() {
    return db.Blogs.aggregate([
        { $match: { "followers" : {$gt : 0}} },
        { $group: { _id: null, total: {$sum: "$followers"} } }
    ]);
}


