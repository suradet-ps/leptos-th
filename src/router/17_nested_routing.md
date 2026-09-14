# การจัดเส้นทางแบบซ้อน

เราเพิ่งนิยามชุดเส้นทางต่อไปนี้:

```rust
<Routes fallback=|| "Not found.">
  <Route path=path!("/") view=Home/>
  <Route path=path!("/users") view=Users/>
  <Route path=path!("/users/:id") view=UserProfile/>
  <Route path=path!("/*any") view=|| view! { <h1>"Not Found"</h1> }/>
</Routes>
```

มีส่วนที่ซ้ำซ้อนกันอยู่พอสมควรตรงนี้: `/users` และ `/users/:id` ซึ่งไม่ใช่ปัญหาสำหรับแอปขนาดเล็ก แต่คุณคงบอกได้ทันทีว่ามันจะไม่สามารถรองรับการเติบโตของแอปได้ดีนัก จะดีกว่าไหมถ้าเราสามารถซ้อนเส้นทางเหล่านี้เข้าด้วยกันได้?

แน่นอน... คุณสามารถทำได้!

```rust
<Routes fallback=|| "Not found.">
  <Route path=path!("/") view=Home/>
  <ParentRoute path=path!("/users") view=Users>
    <Route path=path!(":id") view=UserProfile/>
  </ParentRoute>
  <Route path=path!("/*any") view=|| view! { <h1>"Not Found"</h1> }/>
</Routes>
```

คุณสามารถซ้อน `<Route/>` ไว้ภายใน `<ParentRoute/>` ได้ ดูตรงไปตรงมาดี

แต่ช้าก่อน เราเพิ่งเปลี่ยนพฤติกรรมการทำงานของแอปพลิเคชันของเราไปอย่างแนบเนียน

หัวข้อถัดไปนี้ถือเป็นหนึ่งในหัวข้อที่สำคัญที่สุดในส่วนของระบบเราติงทั้งหมดของคู่มือนี้ โปรดอ่านอย่างละเอียด และหากมีจุดใดที่คุณไม่เข้าใจ สามารถสอบถามได้ทันที

# เส้นทางแบบซ้อนในฐานะเลย์เอาต์

เส้นทางแบบซ้อนคือรูปแบบหนึ่งของการจัดเลย์เอาต์ ไม่ใช่วิธีการนิยามเส้นทางเพื่อเขียนพาธให้สั้นลง

ขออธิบายอีกแบบหนึ่ง: เป้าหมายของการนิยามเส้นทางแบบซ้อนไม่ใช่เพื่อหลีกเลี่ยงการเขียนพาธซ้ำ ๆ เป็นหลัก แต่แท้จริงแล้วคือการบอกให้เราเตอร์แสดงคอมโพเนนต์ `<Route/>` หลายตัวบนหน้าเว็บในเวลาเดียวกัน เคียงข้างกัน

ลองย้อนกลับไปดูตัวอย่างจริงของเรา:

```rust
<Routes fallback=|| "Not found.">
  <Route path=path!("/users") view=Users/>
  <Route path=path!("/users/:id") view=UserProfile/>
</Routes>
```

ความหมายของโค้ดนี้คือ:

- หากเราเข้าไปที่ `/users` เราจะได้คอมโพเนนต์ `<Users/>`
- หากเราเข้าไปที่ `/users/3` เราจะได้คอมโพเนนต์ `<UserProfile/>` (โดยพารามิเตอร์ `id` ถูกตั้งค่าเป็น `3` ซึ่งเราจะพูดถึงกันในภายหลัง)

สมมติว่าเราเปลี่ยนมาใช้เส้นทางแบบซ้อนแทน:

```rust
<Routes fallback=|| "Not found.">
  <ParentRoute path=path!("/users") view=Users>
    <Route path=path!(":id") view=UserProfile/>
  </ParentRoute>
</Routes>
```

ความหมายจะเปลี่ยนไปเป็นดังนี้:

- หากเราเข้าไปที่ `/users/3` ตัวพาธจะตรงกับ `<Route/>` สองตัวพร้อมกัน: คือ `<Users/>` และ `<UserProfile/>`
- หากเราเข้าไปที่ `/users` ตัวพาธจะไม่ตรงกับเส้นทางใดเลย

ในความเป็นจริง เราจึงจำเป็นต้องเพิ่มเส้นทางฟอลแบ็กเข้าไปด้วย:

```rust
<Routes>
  <ParentRoute path=path!("/users") view=Users>
    <Route path=path!(":id") view=UserProfile/>
    <Route path=path!("") view=NoUser/>
  </ParentRoute>
</Routes>
```

คราวนี้:

- หากเราเข้าไปที่ `/users/3` พาธจะตรงกับทั้ง `<Users/>` และ `<UserProfile/>`
- หากเราเข้าไปที่ `/users` พาธจะตรงกับทั้ง `<Users/>` และ `<NoUser/>`

พูดอีกอย่างคือ เมื่อเราใช้เส้นทางแบบซ้อน แต่ละ **พาธ (path)** สามารถจับคู่ตรงกับ **เส้นทาง (routes)** ได้หลายตัวพร้อมกัน: แต่ละ URL สามารถเรนเดอร์วิวที่จัดเตรียมโดยคอมโพเนนต์ `<Route/>` หลายตัว ขึ้นมาแสดงบนหน้าเว็บเดียวกันในเวลาเดียวกันได้

เรื่องนี้อาจฟังดูขัดกับสัญชาตญาณในตอนแรก แต่มันทรงพลังมาก ด้วยเหตุผลที่คุณจะได้เห็นในอีกไม่กี่นาทีข้างหน้านี้

## ทำไมต้องจัดเส้นทางแบบซ้อน?

แล้วทำไมเราต้องทำแบบนี้ด้วยล่ะ?

เว็บแอปพลิเคชันส่วนใหญ่จะมีระดับของการนำทาง (levels of navigation) ที่สอดคล้องกับแต่ละส่วนของเลย์เอาต์ ตัวอย่างเช่น ในแอปพลิเคชันอีเมล คุณอาจมี URL เช่น `/contacts/greg` ซึ่งจะแสดงรายชื่อผู้ติดต่อไว้ทางฝั่งซ้ายของหน้าจอ และแสดงรายละเอียดของผู้ติดต่อที่ชื่อ Greg ไว้ทางฝั่งขวาของหน้าจอ ทั้งรายชื่อผู้ติดต่อและรายละเอียดควรปรากฏขึ้นบนหน้าจอพร้อมกันเสมอ และหากยังไม่มีการเลือกผู้ติดต่อคนใด คุณก็อาจต้องการแสดงข้อความแนะนำสั้น ๆ แทน

คุณสามารถนิยามโครงสร้างแบบนี้ได้อย่างง่ายดายด้วยเส้นทางแบบซ้อน:

```rust
<Routes fallback=|| "Not found.">
  <ParentRoute path=path!("/contacts") view=ContactList>
    <Route path=path!(":id") view=ContactInfo/>
    <Route path=path!("") view=|| view! {
      <p>"Select a contact to view more info."</p>
    }/>
  </ParentRoute>
</Routes>
```

คุณยังสามารถซ้อนลึกลงไปได้อีก สมมติว่าคุณต้องการมีแท็บสำหรับดูที่อยู่, อีเมล/โทรศัพท์ และบทสนทนากับผู้ติดต่อแต่ละคน คุณก็สามารถเพิ่มเส้นทางแบบซ้อน *อีกชุดหนึ่ง* ไว้ภายใต้ `:id` ได้:

```rust
<Routes fallback=|| "Not found.">
  <ParentRoute path=path!("/contacts") view=ContactList>
    <ParentRoute path=path!(":id") view=ContactInfo>
      <Route path=path!("") view=EmailAndPhone/>
      <Route path=path!("address") view=Address/>
      <Route path=path!("messages") view=Messages/>
    </ParentRoute>
    <Route path=path!("") view=|| view! {
      <p>"Select a contact to view more info."</p>
    }/>
  </ParentRoute>
</Routes>
```

> หน้าแรกของ [เว็บไซต์ Remix](https://remix.run/) ซึ่งเป็นเฟรมเวิร์ก React จากผู้สร้าง React Router มีตัวอย่างภาพประกอบที่ยอดเยี่ยมมากหากคุณเลื่อนลงไปดู โดยแสดงเส้นทางแบบซ้อน 3 ระดับ: Sales > Invoices > ใบแจ้งหนี้แต่ละใบ

## `<Outlet/>`

เส้นทางแม่จะไม่เรนเดอร์เส้นทางลูกที่ซ้อนอยู่ภายในโดยอัตโนมัติ เพราะอย่างที่ทราบกัน พวกมันเป็นเพียงคอมโพเนนต์ธรรมดา จึงไม่รู้ว่าควรจะนำคอมโพเนนต์ลูกไปเรนเดอร์ไว้ตรงไหน และคำตอบอย่าง "ก็เอาไปแปะไว้ท้ายคอมโพเนนต์แม่สิ" ก็ไม่ใช่วิธีการที่ดีนัก

แต่คุณสามารถบอกคอมโพเนนต์แม่ได้ว่าควรจะเรนเดอร์คอมโพเนนต์ลูกไว้ที่ตำแหน่งใด โดยใช้คอมโพเนนต์ `<Outlet/>` ซึ่ง `<Outlet/>` จะเรนเดอร์สิ่งใดสิ่งหนึ่งจากสองกรณีต่อไปนี้:

- หากไม่มีเส้นทางลูกที่ตรงกับ URL มันจะไม่แสดงผลสิ่งใดเลย
- หากมีเส้นทางลูกที่ตรงกับ URL มันจะเรนเดอร์ `view` ของเส้นทางลูกนั้นขึ้นมา

มีเพียงแค่นี้เอง! แต่นี่เป็นเรื่องสำคัญมากที่ต้องจำไว้ เพราะเป็นสาเหตุยอดฮิตที่ทำให้เกิดคำถามว่า "ทำไมมันไม่ทำงาน?" หากคุณไม่ได้ใส่คอมโพเนนต์ `<Outlet/>` เอาไว้ เส้นทางลูกที่ซ้อนอยู่ก็จะไม่ถูกนำมาแสดงผลเลย

```rust
#[component]
pub fn ContactList() -> impl IntoView {
  let contacts = todo!();

  view! {
    <div style="display: flex">
      // the contact list
      <For each=contacts
        key=|contact| contact.id
        children=|contact| todo!()
      />
      // the nested child, if any
      // don’t forget this!
      <Outlet/>
    </div>
  }
}
```

## การรีแฟกเตอร์การนิยามเส้นทาง

คุณไม่จำเป็นต้องนิยามเส้นทางทั้งหมดไว้ในที่เดียวหากคุณไม่ต้องการ คุณสามารถแยก `<Route/>` ใด ๆ พร้อมด้วยคอมโพเนนต์ลูกของมัน ออกไปเป็นคอมโพเนนต์ย่อยอีกตัวหนึ่งได้

ตัวอย่างเช่น คุณสามารถรีแฟกเตอร์โค้ดตัวอย่างข้างต้นให้แยกออกเป็น 2 คอมโพเนนต์ดังนี้:

```rust
#[component]
pub fn App() -> impl IntoView {
    view! {
      <Router>
        <Routes fallback=|| "Not found.">
          <ParentRoute path=path!("/contacts") view=ContactList>
            <ContactInfoRoutes/>
            <Route path=path!("") view=|| view! {
              <p>"Select a contact to view more info."</p>
            }/>
          </ParentRoute>
        </Routes>
      </Router>
    }
}

#[component(transparent)]
fn ContactInfoRoutes() -> impl MatchNestedRoutes + Clone {
    view! {
      <ParentRoute path=path!(":id") view=ContactInfo>
        <Route path=path!("") view=EmailAndPhone/>
        <Route path=path!("address") view=Address/>
        <Route path=path!("messages") view=Messages/>
      </ParentRoute>
    }
    .into_inner()
    .into_any_nested_route()
}
```

คอมโพเนนต์ตัวที่สองนี้เป็น `#[component(transparent)]` ซึ่งหมายความว่ามันจะคืนค่าเพียงแค่ข้อมูลของมันเท่านั้น ไม่ใช่วิว และในทำนองเดียวกัน มันใช้ `.into_inner()` เพื่อตัดข้อมูลสำหรับการดีบักที่แมโคร `view` ใส่เพิ่มเข้ามาออกไป และคืนค่าเฉพาะคำนิยามเส้นทางที่สร้างขึ้นโดย `<ParentRoute/>` เท่านั้น

## การจัดเส้นทางแบบซ้อนและประสิทธิภาพ

ทั้งหมดนี้ฟังดูดีในเชิงแนวคิด แต่คำถามคือ—แล้วมันมีประโยชน์อย่างไรกันแน่?

ประสิทธิภาพ

ในไลบรารีที่ใช้การอัปเดตเชิงรีแอกทีฟแบบละเอียดระดับย่อย (fine-grained reactive library) อย่าง Leptos สิ่งสำคัญที่สุดเสมอคือการลดปริมาณงานในการเรนเดอร์ให้เหลือน้อยที่สุดเท่าที่จะเป็นไปได้ เพราะเราทำงานกับโหนด DOM จริงโดยตรง ไม่ได้ทำการ diff บน virtual DOM ดังนั้นเราจึงต้องการ "เรนเดอร์ใหม่" (rerender) คอมโพเนนต์ให้น้อยครั้งที่สุดเท่าที่จะทำได้ ซึ่งการจัดเส้นทางแบบซ้อนช่วยให้เรื่องนี้เป็นเรื่องง่ายดายมาก

ลองนึกภาพตัวอย่างรายชื่อผู้ติดต่อ หากเราคลิกเปลี่ยนจาก Greg ไปเป็น Alice แล้วไป Bob จากนั้นกลับมาที่ Greg ข้อมูลของผู้ติดต่อย่อมต้องเปลี่ยนไปในการนำทางแต่ละครั้ง แต่คอมโพเนนต์ `<ContactList/>` ไม่ควรจะต้องถูกเรนเดอร์ใหม่เลยแม้แต่น้อย สิ่งนี้ไม่เพียงแต่ช่วยประหยัดการทำงานในการเรนเดอร์เท่านั้น แต่ยังช่วยรักษาสถานะของ UI เอาไว้ด้วย ตัวอย่างเช่น หากคุณมีช่องค้นหาอยู่ที่ด้านบนของ `<ContactList/>` การคลิกเปลี่ยนจาก Greg ไป Alice แล้วไป Bob จะไม่ทำให้คำค้นหาที่พิมพ์ค้างไว้หายไป

ยิ่งไปกว่านั้น ในกรณีนี้ เราไม่จำเป็นต้องเรนเดอร์คอมโพเนนต์ `<Contact/>` ใหม่เลยด้วยซ้ำเมื่อย้ายสลับระหว่างผู้ติดต่อ เพราะเราเตอร์จะคอยอัปเดตพารามิเตอร์ `:id` แบบรีแอกทีฟให้โดยอัตโนมัติในขณะที่เรานำทาง ทำให้เราสามารถทำการอัปเดตแบบละเอียดเฉพาะจุดได้: เมื่อเราย้ายไปมาระหว่างผู้ติดต่อ เราจะอัปเดตเพียงโหนดข้อความเดี่ยวเพื่อเปลี่ยนชื่อ ที่อยู่ และอื่น ๆ ของผู้ติดต่อ โดยไม่ต้องมีการเรนเดอร์ส่วนอื่นใหม่*เพิ่มเติมเลยแม้แต่น้อย*

> แซนด์บ็อกซ์นี้มีฟีเจอร์หลายอย่าง (เช่น การจัดเส้นทางแบบซ้อน) ที่เราได้คุยกันไปในหัวข้อนี้และหัวข้อก่อนหน้า รวมถึงอีกหลายฟีเจอร์ที่เรากำลังจะพูดถึงในส่วนที่เหลือของบทนี้ เนื่องจากเราเตอร์เป็นระบบที่มีการทำงานเชื่อมโยงกันอย่างมาก การยกตัวอย่างชุดเดียวที่ครอบคลุมจึงเหมาะสมที่สุด ดังนั้นไม่ต้องแปลกใจหากมีบางจุดที่คุณยังไม่เข้าใจในทันที

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox.](https://codesandbox.io/p/devbox/16-router-0-7-csm8t5?file=%2Fsrc%2Fmain.rs)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/16-router-0-7-csm8t5?file=%2Fsrc%2Fmain.rs" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;
use leptos_router::components::{Outlet, ParentRoute, Route, Router, Routes, A};
use leptos_router::hooks::use_params_map;
use leptos_router::path;

#[component]
pub fn App() -> impl IntoView {
    view! {
        <Router>
            <h1>"Contact App"</h1>
            // this <nav> will show on every routes,
            // because it's outside the <Routes/>
            // note: we can just use normal <a> tags
            // and the router will use client-side navigation
            <nav>
                <a href="/">"Home"</a>
                <a href="/contacts">"Contacts"</a>
            </nav>
            <main>
                <Routes fallback=|| "Not found.">
                    // / just has an un-nested "Home"
                    <Route path=path!("/") view=|| view! {
                        <h3>"Home"</h3>
                    }/>
                    // /contacts has nested routes
                    <ParentRoute
                        path=path!("/contacts")
                        view=ContactList
                      >
                        // if no id specified, fall back
                        <ParentRoute path=path!(":id") view=ContactInfo>
                            <Route path=path!("") view=|| view! {
                                <div class="tab">
                                    "(Contact Info)"
                                </div>
                            }/>
                            <Route path=path!("conversations") view=|| view! {
                                <div class="tab">
                                    "(Conversations)"
                                </div>
                            }/>
                        </ParentRoute>
                        // if no id specified, fall back
                        <Route path=path!("") view=|| view! {
                            <div class="select-user">
                                "Select a user to view contact info."
                            </div>
                        }/>
                    </ParentRoute>
                </Routes>
            </main>
        </Router>
    }
}

#[component]
fn ContactList() -> impl IntoView {
    view! {
        <div class="contact-list">
            // here's our contact list component itself
            <h3>"Contacts"</h3>
            <div class="contact-list-contacts">
                <A href="alice">"Alice"</A>
                <A href="bob">"Bob"</A>
                <A href="steve">"Steve"</A>
            </div>

            // <Outlet/> will show the nested child route
            // we can position this outlet wherever we want
            // within the layout
            <Outlet/>
        </div>
    }
}

#[component]
fn ContactInfo() -> impl IntoView {
    // we can access the :id param reactively with `use_params_map`
    let params = use_params_map();
    let id = move || params.read().get("id").unwrap_or_default();

    // imagine we're loading data from an API here
    let name = move || match id().as_str() {
        "alice" => "Alice",
        "bob" => "Bob",
        "steve" => "Steve",
        _ => "User not found.",
    };

    view! {
        <h4>{name}</h4>
        <div class="contact-info">
            <div class="tabs">
                <A href="" exact=true>"Contact Info"</A>
                <A href="conversations">"Conversations"</A>
            </div>

            // <Outlet/> here is the tabs that are nested
            // underneath the /contacts/:id route
            <Outlet/>
        </div>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
