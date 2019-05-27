
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

function statistics() {
    return db.Blogs.aggregate([
        { $group: {
            _id: null,
            followers: {$sum: "$followers"},
            views: {$sum: "$views"},
            articles_amount: {$sum: "$articles_amount"}
        }}
    ]);
}

function categoryStatistics()
{
    return db.Blogs.aggregate([
        {$unwind: "$articles"},
        {$group: {
            _id: '$articles.categories',
            total: {$sum: 1}
        }}
    ]);
}

function articlesPerBlog()
{
    return db.Blogs.aggregate([
        {$group: {
            _id: '$blog_name',
            total: {$sum: "$articles_amount"}
        }},
        {$sort: {total: -1}}
    ]);
}

function commentsPerBlog()
{
    return db.Blogs.aggregate([
        {$project: {
            _id: '$blog_name',
            count: {$size: "$articles.comments"},
        }},
        {$sort: {count: -1}}
    ]);
}

