from django.db import models
from django.template.defaultfilters import slugify
#users
from django.contrib.auth.models import User
#tags
#from taggit_autocomplete.managers import TaggableManager
from taggit_autosuggest.managers import TaggableManager
#ratings
from djangoratings.fields import RatingField
from datetime import datetime




class CommonInfo(models.Model):
    name            = models.CharField(max_length=512, unique=True, null=False, blank=False, help_text='The name must be unique', verbose_name = 'Name or Title')
    description     = models.TextField(blank=True)
    published       = models.BooleanField()
    tags            = TaggableManager(blank = True)
    creation_time   = models.DateTimeField() # generated in save
    update_time     = models.DateTimeField() # generated in save
    slug            = models.SlugField(max_length=512, unique=True, blank=True)
    
    def save(self):
        if not self.id:
            self.creation_time = datetime.now()
            self.slug = slugify("{0} {1}".format(self.name, self.creation_time.date().isoformat()))
        self.update_time = datetime.now()
        super(CommonInfo, self).save()
        
        
    class Meta:
        abstract = True
        ordering = ['-creation_time'] #this doesn't seem to work.



OS_CHOICES = (
    ('Windows', 'Windows'),
    ('Mac', 'Mac'),
    ('Linux', 'Linux'),
)

RATING_CHOICES = (
    (0,0),
    (1,1),
    (2,2),
    (3,3),
    (4,4),
    (5,5),
)

DOCUMENT_KIND_CHOICES = (
    ('audio','audio'),
    ('video','video'),
    ('image','image'),
    ('text','text'),
    ('database','database'),
)


class Review(CommonInfo):
    product              = models.ForeignKey(to='Product')
    reviewer             = models.ForeignKey(to=User)
    editor               = models.ForeignKey(to=User, null=True, blank=True, related_name='review_editor_user')
    kicker               = models.CharField(max_length = 128, blank = True)
    subtitle             = models.CharField(max_length = 512, blank = True)
    teaser               = models.TextField(blank = True)
    user_rating          = RatingField(range=10, allow_anonymous = True, use_cookies = True)
    version_tested       = models.CharField(max_length=128, blank = True)
    os_used              = models.ManyToManyField('OperatingSystem', blank = True, null = True)
    review_done          = models.DateField(null = True, blank=True)
    image                = models.ImageField( help_text='Review Screenshot? TODO: Standardize Size', max_length=256,
                                            upload_to='review_lab/contrib/img/reviews', null=True, blank=True)
    
    community            = models.IntegerField(choices=RATING_CHOICES, default = 0)
    community_text       = models.CharField(max_length = 256, blank = True)
    documentation        = models.IntegerField(choices=RATING_CHOICES, default = 0)
    documentation_text   = models.CharField(max_length = 256, blank = True)
    performance          = models.IntegerField(choices=RATING_CHOICES, default = 0)
    performance_text     = models.CharField(max_length = 256, blank = True)
    usability            = models.IntegerField(choices=RATING_CHOICES, default = 0, help_text = "General Difficulty level, learning curve.")
    usability_text       = models.CharField(max_length = 256, blank = True)
    rating               = models.IntegerField(choices=RATING_CHOICES, default = 0)
    rating_text          = models.CharField(max_length = 256, blank = True)
        
    def __unicode__(self):
        return u'%s (Review of: %s)' % (self.name, self.product)
    
    @models.permalink
    def get_absolute_url(self):
        return ('review_view', (), {'slug': self.slug})
        
    class Meta:
        ordering = ['-creation_time']
    
    
    
class Product(CommonInfo):
    url                                   = models.URLField(blank=True)
    image                                 = models.ImageField( help_text='Product logo or screenshot. TODO: Standardize Size', max_length=256,
                                                              upload_to='review_lab/contrib/img/products', null=True, blank=True)
    cost                                  = models.IntegerField(blank=False, default=0,help_text='Cost is a dollar amount. "0" for free')
    categories                            = models.ManyToManyField('Category', blank=True, null=True)
    programming_required_rating           = models.IntegerField(choices=RATING_CHOICES, default = 0)
    programming_required_description      = models.TextField(blank = True)
    tasks_performed                       = models.ManyToManyField(to='Task', through='ProductTask', blank=True, null=True)
    open_source                           = models.BooleanField()
    demo_available                        = models.BooleanField()
    company                               = models.CharField(max_length = 128, blank = True)
    release_date                          = models.DateField(null = True, blank=True)
    obsolete                              = models.BooleanField()
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.url)
        
    @models.permalink
    def get_absolute_url(self):
        return ('product_view', (), {'slug': self.slug})

    class Meta:
        ordering = ['-creation_time']



class Tutorial(CommonInfo):
    product              = models.ForeignKey(to='Product')
    url                  = models.URLField(blank=True, help_text='URL to source of this tutorial if applicable.')
    tasks                = models.ManyToManyField('Task', blank=True, null=True, help_text='What tasks this tutorial will help with')
    writer               = models.ForeignKey(to=User, null=True, blank=True)
    writer_external      = models.CharField(max_length = 256, blank=True, help_text='Writer name, email if not part of Review Lab')
    editor               = models.ForeignKey(to=User, null=True, blank=True, related_name='tutorial_editor_user')
    kicker               = models.CharField(max_length = 128, blank = True)
    subtitle             = models.CharField(max_length = 512, blank = True)
    teaser               = models.TextField(blank = True)
    image                = models.ImageField( help_text='Product logo or screenshot. TODO: Standardize Size', max_length=256,
                                              upload_to='review_lab/contrib/img/tutorials', null=True, blank=True)
    embed                = models.TextField(help_text='This is probably a YouTube Embed or something similar.', blank=True)
    repo_link            = models.URLField(verbose_name='Repository Link', blank=True)
    files                = models.FileField(verbose_name='Tutorial Zip File', upload_to='review_lab/contrib/zip/tutorial_files', blank=True, null=True)
    
    
    @models.permalink
    def get_absolute_url(self):
        return ('tutorial_view', (), {'slug': self.slug})
    

    class Meta:
        ordering = ['-creation_time']


class Challenge(CommonInfo):
    tasks                     = models.ManyToManyField(to='Task', blank=True, null=True)
    documents                 = models.ManyToManyField(to='DocumentSet', blank=True, null=True)
    teaser                    = models.TextField(blank=True)
    kicker                    = models.CharField(max_length = 128, blank = True)
    subtitle                  = models.CharField(max_length = 512, blank = True)
    image                     = models.ImageField(help_text='Challenge logo. TODO: Standardize Size', max_length=256,
                                            upload_to='review_lab/contrig/img/challenges', null=True, blank=True)
    files                     = models.FileField(verbose_name='Challenge Files', upload_to='review_lab/contrib/zip/challenges', blank=True, null=True,
                                           help_text='Any kind of related files for the challenge should go here if not part of the Document Set')
    contact                   = models.ForeignKey(to=User, null=True, blank=True)
    other_contact             = models.CharField(max_length=256, blank=True, help_text='other contact information if not user in system')
    award                     = models.CharField(max_length=256, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('challenge_view', (), {'slug': self.slug})
        
    class Meta:
        ordering = ['-creation_time']

    
class Task(CommonInfo):
    document = models.ForeignKey('DocumentSet', null=True)
    
    def document_name(self):
        return self.document.name
    
    def __unicode__(self):
        return u'Task: %s, For Document: %s' % (self.name, self.document)
        
    @models.permalink
    def get_absolute_url(self):
        return ('task_view', (), {'slug': self.slug})    

    class Meta:
        ordering = ['-creation_time']


class ProductTask(CommonInfo):
    product       = models.ForeignKey('Product')
    task          = models.ForeignKey('Task')
    rating        = models.IntegerField(choices=RATING_CHOICES, default = 0)
    rating_text   = models.CharField(max_length = 256, blank = True)
    
    def __unicode__(self):
        return u'Task Review of %s for Task %s' % (self.product, self.task)
    
    def product_name(self):
        return self.product.name
    
    def task_name(self):
        return self.task.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('product_task_view', (), {'slug': self.slug})
    
    class Meta:
        verbose_name = 'Product Task Review'
        verbose_name_plural = 'Product Task Reviews'
        ordering = ['-creation_time']


class DocumentSet(CommonInfo):
    url       = models.URLField(blank=True)
    kind      = models.CharField(max_length=64, choices=DOCUMENT_KIND_CHOICES)
    image     = models.ImageField( help_text='Sample Document Image or logo of some sort. TODO: Standardize Size', max_length=256,
                                   upload_to='review_lab/contrib/img/docs', null=True, blank=True)
    
    
    def __unicode__(self):
        return u'%s' % (self.name,)
        
    @models.permalink
    def get_absolute_url(self):
        return ('document_view', (), {'slug': self.slug})
        
    
    class Meta:
        verbose_name = 'Document Set'
        verbose_name_plural = 'Document Sets'
        ordering = ['-creation_time']












class Category(CommonInfo):
    
    def __unicode__(self):
        return u'%s' % (self.name,)
        
    class Meta:
        verbose_name_plural = 'Categories'
    
    

class OperatingSystem(CommonInfo):
    url = models.URLField(blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.name,)
        
    class Meta:
        verbose_name = 'Operating System'
        verbose_name_plural = 'Operating Systems'




    